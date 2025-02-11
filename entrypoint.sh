#!/usr/bin/env bash
chown -R 0:0 /course_data || true
exec flask run --host=0.0.0.0
