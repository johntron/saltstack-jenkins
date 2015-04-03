from __future__ import absolute_import

import re
import logging
import requests
import os
import os.path

import salt.ext.six.moves.http_client

log = logging.getLogger(__name__)

def _error(ret, msg):
  ret['result'] = False
  ret['changes'] = {}
  ret['comment'] = msg
  return ret

def _write(filename, response):
  with open(filename, 'wb') as handle:
    for block in response.iter_content(1024):
      if not block:
        break

      handle.write(block)


def artifact_present(name, project_url, job='lastSuccessfulBuild', re_match=None, cwd=None, save_as=None):
  '''
    Download a single artifact from Jenkins job
  '''

  ret = {
    'name': name,
    'changes': {},
    'comment': ''
  }

  # Guards
  if not name and not re_match:
    return _error(ret, 'Cannot determine which artifact to use. Please use one of: name, re_match')

  url = '{0}/{1}/api/json'.format(project_url, job)
  log.info('Querying {0}'.format(url))
  response = requests.get(url)

  if response.status_code == salt.ext.six.moves.http_client.OK:
    data = response.json()
  elif response.status_code == salt.ext.six.moves.http_client.UNAUTHORIZED:
    log.error('Authentication failed. Please check the configuration.')
  elif response.status_code == salt.ext.six.moves.http_client.NOT_FOUND:
    log.error('URL {0} was not found.'.format(url))
  else:
    log.debug('Results: {0}'.format(response.text))

  log.info('Artifacts: {0}'.format(data['artifacts']))

  if re_match:
    log.info('Looking for artifacts matching {0}'.format(re_match))
    artifacts = [a for a in data['artifacts'] if re.match(re_match, a['fileName'])]
  else:
    log.info('Looking for artifacts: {0}'.format(name))
    artifacts = [a for a in data['artifacts'] if a['fileName'] == name]

  log.info('Matched artifacts: {0}'.format(artifacts))

  if not artifacts:
    return _error(ret, 'No artifacts found matching name/re_match')

  if len(artifacts) > 1:
    filenames = ', '.join([a['fileName'] for a in artifacts])
    return _error(ret, 'Found more than one artifact matching criteria: {0}'.format(filenames))

  artifact = artifacts[0]
  path = cwd or os.path.expanduser('~')
  filename = os.path.join(path, save_as or name)
  url = '{0}/{1}/artifact/{2}'.format(project_url, job, artifact['relativePath'])

  log.info('Downloading artifact from {0}'.format(url))
  result = requests.get(url, stream=True)

  if response.status_code == salt.ext.six.moves.http_client.UNAUTHORIZED:
    log.error('Authentication failed. Please check the configuration.')
  elif response.status_code == salt.ext.six.moves.http_client.NOT_FOUND:
    log.error('URL {0} was not found.'.format(url))

  log.info('Writing to {0}'.format(filename))

  _write(filename, result)

  ret['result'] = True
  return ret
