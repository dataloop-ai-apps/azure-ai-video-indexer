import subprocess
import json
import time
import base64

import dtlpy as dl


def bump(bump_type='patch'):
    print(f"Bump Time: {time.time()}")
    subprocess.run(f'bumpversion {bump_type} --allow-dirty', shell=True)


def create_org_secret(project):
    org: dl.Organization = project.org
    with open('.env') as f:
        params = json.load(f)
        secrets = base64.b64encode(json.dumps(params).encode('ascii'))
    org.integrations.create(integrations_type=dl.IntegrationType.KEY_VALUE,
                            name='azure-indexer-secrets',
                            options=secrets)


def publish_and_install(project, manifest):
    env = dl.environment()
    app_name = manifest['name']
    app_version = manifest['version']
    print(f'Publishing and installing {app_name} {app_version} to project {project.name} in {env}')

    # publish dpk to app store
    dpk = project.dpks.publish(ignore_max_file_size=True)
    print(f'published successfully! dpk name: {dpk.name}, version: {dpk.version}, dpk id: {dpk.id}')
    try:
        app = project.apps.get(app_name=dpk.display_name)
        print(f'already installed, updating...')
        app.dpk_version = dpk.version
        app.update()
        print(f'update done. app id: {app.id}')
    except dl.exceptions.NotFound:
        print(f'installing ..')

        app = project.apps.install(dpk=dpk,
                                   app_name=dpk.display_name,
                                   scope=dl.AppScope.SYSTEM)
        print(f'installed! app id: {app.id}')
    print(f'Done!')


if __name__ == "__main__":
    dl.setenv('rc')
    project = dl.projects.get(project_id='2cb9ae90-b6e8-4d15-9016-17bacc9b7bdf')  # DataloopApps
    bump()

    with open('dataloop.json') as f:
        manifest = json.load(f)

    publish_and_install(manifest=manifest, project=project)
