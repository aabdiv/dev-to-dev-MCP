#!/bin/bash
set -e

case "$1" in
    serve)
        echo "🚀 Starting MCP server on port 8000..."
        echo "   - /health → Health check endpoint"
        echo "   - /mcp    → MCP protocol endpoint"
        echo ""
        exec git-changelog-mcp
        ;;
    
    smoke)
        echo "🏥 Running smoke test..."
        echo ""
        
        # Запуск сервера в фоне
        git-changelog-mcp &
        SERVER_PID=$!
        
        # Функция очистки при выходе
        cleanup() {
            echo ""
            echo "🛑 Stopping server..."
            kill $SERVER_PID 2>/dev/null || true
            wait $SERVER_PID 2>/dev/null || true
        }
        trap cleanup EXIT
        
        # Ждём старта сервера
        echo "⏳ Waiting for server to start (max 30s)..."
        for i in $(seq 1 30); do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                echo "✅ Server started after ${i}s"
                break
            fi
            if [ $i -eq 30 ]; then
                echo "❌ Server failed to start within 30s"
                exit 1
            fi
            sleep 1
        done
        
        # Проверка health endpoint
        echo ""
        echo "🔍 Checking health endpoint..."
        HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" \
            --connect-timeout 5 \
            http://localhost:8000/health)
        
        echo "   HTTP Status: $HTTP_CODE"
        
        # Показываем ответ
        if [ -f /tmp/health_response.json ]; then
            echo "   Response: $(cat /tmp/health_response.json)"
        fi
        
        echo ""
        
        # Результат
        if [ "$HTTP_CODE" = "200" ]; then
            echo "✅ Smoke test PASSED (HTTP $HTTP_CODE)"
            exit 0
        else
            echo "❌ Smoke test FAILED (HTTP $HTTP_CODE)"
            echo ""
            echo "Диагностика:"
            echo "   1. Проверьте логи сервера выше"
            echo "   2. Убедитесь что порт 8000 не занят"
            echo "   3. Проверьте что git-changelog-mcp установлен"
            exit 1
        fi
        ;;
    
    help|--help|-h)
        echo "Usage: entrypoint.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  serve    Start MCP server (default)"
        echo "  smoke    Run smoke test"
        echo "  help     Show this help message"
        ;;
    
    *)
        echo "❌ Unknown command: $1" >&2
        echo "" >&2
        echo "Usage: entrypoint.sh [serve|smoke|help]" >&2
        exit 1
        ;;
esac
