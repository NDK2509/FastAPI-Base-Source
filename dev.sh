#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${ROOT_DIR}/app"
DOCKER_DIR="${ROOT_DIR}/docker"
COMPOSE_FILE="${DOCKER_DIR}/docker-compose.yml"
DOCKER_ENV_FILE="${DOCKER_DIR}/.env"
DOCKER_ENV_SAMPLE="${DOCKER_DIR}/.env.sample"
LOCAL_ENV_FILE="${ROOT_DIR}/.env"
LOCAL_ENV_EXAMPLE="${ROOT_DIR}/.env.example"

usage() {
    cat <<'EOF'
Usage: ./dev.sh <command> [options/args...]

Commands:
  start [--build] [services...]   Start Docker Compose services in detached mode
  restart [--build] [services...] Down and up Docker Compose services (rebuild with --build)
  stop [services...]              Stop running Docker Compose services
  down [options...]               Stop and remove containers and networks
  logs [services...]              Follow logs for all or specified services
  ps | status                     Show status of Docker Compose services
  migrate [--local] [args...]     Run Alembic migrations (default: upgrade head)
                                  Use 'migrate create "<msg>"' for autogenerate revision
  tests | test [pytest_args...]   Run pytest suite using local virtualenv
  help                            Show this help message

Examples:
  ./dev.sh start
  ./dev.sh start --build app
  ./dev.sh restart app
  ./dev.sh logs app
  ./dev.sh migrate
  ./dev.sh migrate create "add user phone column"
  ./dev.sh migrate downgrade -1
  ./dev.sh migrate --local current
  ./dev.sh tests -v
  ./dev.sh tests --cov=app --cov-report=term-missing
EOF
}

log_info() {
    printf '[dev] %s\n' "$*"
}

log_error() {
    printf '[dev] ERROR: %s\n' "$*" >&2
}

compose() {
    local compose_args=(-f "${COMPOSE_FILE}")
    if [[ -f "${DOCKER_ENV_FILE}" ]]; then
        compose_args+=(--env-file "${DOCKER_ENV_FILE}")
    fi

    if docker compose version >/dev/null 2>&1; then
        docker compose "${compose_args[@]}" "$@"
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose "${compose_args[@]}" "$@"
    else
        log_error "Docker Compose is not installed ('docker compose' or 'docker-compose' not found)."
        exit 1
    fi
}

check_env_file() {
    if [[ ! -f "${DOCKER_ENV_FILE}" ]]; then
        log_error "Missing ${DOCKER_ENV_FILE}. Copy ${DOCKER_ENV_SAMPLE} to ${DOCKER_ENV_FILE} and configure it first."
        exit 1
    fi
}

check_local_env_file() {
    if [[ ! -f "${LOCAL_ENV_FILE}" ]]; then
        log_error "Missing ${LOCAL_ENV_FILE}. Copy ${LOCAL_ENV_EXAMPLE} to ${LOCAL_ENV_FILE} and configure it first."
        exit 1
    fi
}

resolve_venv_bin() {
    local bin_name="$1"
    if [[ -x "${ROOT_DIR}/.venv/bin/${bin_name}" ]]; then
        printf '%s\n' "${ROOT_DIR}/.venv/bin/${bin_name}"
    elif [[ -x "${ROOT_DIR}/venv/bin/${bin_name}" ]]; then
        printf '%s\n' "${ROOT_DIR}/venv/bin/${bin_name}"
    elif command -v "${bin_name}" >/dev/null 2>&1; then
        command -v "${bin_name}"
    else
        log_error "'${bin_name}' not found in .venv, venv, or PATH."
        exit 1
    fi
}

is_app_running() {
    compose ps --status running --services 2>/dev/null | grep -qx "app"
}

print_urls() {
    if is_app_running; then
        log_info "Swagger UI: http://localhost:8080/docs"
        log_info "ReDoc:      http://localhost:8080/redoc"
    fi
}

cmd_start() {
    check_env_file
    log_info "Starting services..."
    compose up -d "$@"
    print_urls
}

cmd_restart() {
    check_env_file
    local up_args=()
    for arg in "$@"; do
        if [[ "${arg}" == "--build" || "${arg}" == "-b" ]]; then
            up_args+=(--build)
        else
            up_args+=("${arg}")
        fi
    done

    log_info "Tearing down and recreating services..."
    compose down
    compose up -d "${up_args[@]}"
    compose ps
    print_urls
}

cmd_stop() {
    log_info "Stopping services..."
    compose stop "$@"
}

cmd_down() {
    log_info "Stopping and removing containers/networks..."
    compose down "$@"
}

cmd_logs() {
    compose logs -f --tail=100 "$@"
}

cmd_ps() {
    compose ps "$@"
    print_urls
}

cmd_migrate() {
    local use_local=false
    local args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --local)
                use_local=true
                shift
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done

    if [[ ${#args[@]} -eq 0 ]]; then
        args=("upgrade" "head")
    elif [[ "${args[0]}" == "create" ]]; then
        if [[ ${#args[@]} -lt 2 || -z "${args[1]}" ]]; then
            log_error "Migration message required. Usage: ./dev.sh migrate create \"<message>\""
            exit 1
        fi
        args=("revision" "--autogenerate" "-m" "${args[1]}")
    fi

    if [[ "${use_local}" == true ]]; then
        check_local_env_file
        local alembic_bin
        alembic_bin="$(resolve_venv_bin "alembic")"
        log_info "Running local Alembic: alembic ${args[*]}"
        (cd "${APP_DIR}" && "${alembic_bin}" "${args[@]}")
    elif is_app_running; then
        check_env_file
        log_info "Running Alembic inside running 'app' container: alembic ${args[*]}"
        compose exec app alembic "${args[@]}"
    else
        check_env_file
        log_info "'app' container is not running; running Alembic in ephemeral container: alembic ${args[*]}"
        compose run --rm app alembic "${args[@]}"
    fi
}

cmd_tests() {
    local pytest_bin
    pytest_bin="$(resolve_venv_bin "pytest")"
    log_info "Running tests with ${pytest_bin}..."
    (cd "${ROOT_DIR}" && "${pytest_bin}" "$@")
}

main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi

    local command="$1"
    shift

    case "${command}" in
        start)
            cmd_start "$@"
            ;;
        restart)
            cmd_restart "$@"
            ;;
        stop)
            cmd_stop "$@"
            ;;
        down)
            cmd_down "$@"
            ;;
        logs)
            cmd_logs "$@"
            ;;
        ps|status)
            cmd_ps "$@"
            ;;
        migrate)
            cmd_migrate "$@"
            ;;
        tests|test)
            cmd_tests "$@"
            ;;
        help|-h|--help)
            usage
            ;;
        *)
            log_error "Unknown command: ${command}"
            usage
            exit 1
            ;;
    esac
}

main "$@"
