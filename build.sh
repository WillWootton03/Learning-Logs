set -e

echo "Building Tailwind"
python manage.py tailwind build

echo "Collection static files"
python manage.py collectstatic --noinput