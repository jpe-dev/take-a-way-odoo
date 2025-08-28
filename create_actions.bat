@echo off
echo ========================================
echo Creation des actions heure prevue
echo ========================================
echo.

docker-compose exec web odoo shell -d db-odoo-ta -c /etc/odoo/odoo.conf < addons/take_a_way_loyalty/fix_actions.py

echo.
echo ========================================
echo Script termine!
echo ========================================
pause 