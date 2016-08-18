cd /home/song/proj/a/gongfu && setsid /home/song/.virtualenvs/gongfu/bin/python manage.py runworker &
setsid /home/song/.virtualenvs/gongfu/bin/daphne gongfu.asgi:channel_layer -b0.0.0.0 -p80 &