@echo off
echo ========================================
echo Creation des actions heure prevue
echo ========================================
echo.

echo Lancement du shell Odoo...
echo Copiez et collez le contenu du fichier simple_check.py dans le shell
echo.

docker-compose exec web odoo shell -d db-odoo-ta -c /etc/odoo/odoo.conf

echo.
echo ========================================
echo Script termine!
echo ========================================
pause 