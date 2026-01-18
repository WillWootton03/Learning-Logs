cd theme
npm install

echo "Building Tailwind CSS"
npx tailwindcss -i ./static_src/src/styles.css -o ./static/css/dist/styles.css --minify

cd ..
echo "Collection static files"
python manage.py collectstatic --noinput