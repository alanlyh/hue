#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule

from desktop.lib.scheduler.lib.api import Api


class CeleryBeatApi(Api):

  def submit_schedule(self, request, coordinator, mapping):
    is_cron = True # IntervalSchedule is buggy https://github.com/celery/django-celery-beat/issues/279

    if is_cron:
      schedule, created = CrontabSchedule.objects.get_or_create(
          minute='*',
          hour='*',
          day_of_week='*',
          day_of_month='*',
          month_of_year='*'
      )

      task = PeriodicTask.objects.update_or_create(
        crontab=schedule,
        name='Scheduled query N',
        task='notebook.tasks.run_sync_query',
        defaults={"args": json.dumps(['a7428a99-2f77-cf3a-ebbd-460f19ba46cc', request.user.username])},
      )
      task.enabled=True
      task.save()
    else:
      schedule, created = IntervalSchedule.objects.get_or_create(
        every=15,
        period=IntervalSchedule.SECONDS,
      )

      task, created = PeriodicTask.objects.update_or_create(
        interval=schedule,
        name='Scheduled query',
        task='notebook.tasks.run_sync_query',
      )