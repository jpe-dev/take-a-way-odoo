@echo off
echo ========================================
echo Verification des actions heure prevue
echo ========================================
echo.

echo 1. Verification des actions existantes...
docker-compose exec web python3 -c "exec(open('/mnt/extra-addons/take_a_way_loyalty/check_actions.py').read())"

echo.
echo ========================================
echo 2. Creation des actions si necessaire...
echo ========================================
echo.

docker-compose exec web python3 -c "exec(open('/mnt/extra-addons/take_a_way_loyalty/create_actions_sql.py').read())"

echo.
echo ========================================
echo Script termine!
echo ========================================
pause 