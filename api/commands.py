import datetime
import json
import logging
import random
import string

import click
from llama_index.data_structs.node_v2 import DocumentRelationship, Node

from core.index.vector_index import VectorIndex
from extensions.ext_redis import redis_client
from extensions.ext_vector_store import vector_store
from libs.password import password_pattern, valid_password, hash_password
from libs.helper import email as email_validate
from extensions.ext_database import db
from models.account import InvitationCode
from models.dataset import Dataset, Document, DocumentSegment
from models.model import Account, AppModelConfig, ApiToken, Site, App, RecommendedApp
import secrets
import base64


@click.command('reset-password', help='Reset the account password.')
@click.option('--email', prompt=True, help='The email address of the account whose password you need to reset')
@click.option('--new-password', prompt=True, help='the new password.')
@click.option('--password-confirm', prompt=True, help='the new password confirm.')
def reset_password(email, new_password, password_confirm):
    if str(new_password).strip() != str(password_confirm).strip():
        click.echo(click.style('sorry. The two passwords do not match.', fg='red'))
        return
    account = db.session.query(Account). \
        filter(Account.email == email). \
        one_or_none()
    if not account:
        click.echo(click.style('sorry. the account: [{}] not exist .'.format(email), fg='red'))
        return
    try:
        valid_password(new_password)
    except:
        click.echo(
            click.style('sorry. The passwords must match {} '.format(password_pattern), fg='red'))
        return

    # generate password salt
    salt = secrets.token_bytes(16)
    base64_salt = base64.b64encode(salt).decode()

    # encrypt password with salt
    password_hashed = hash_password(new_password, salt)
    base64_password_hashed = base64.b64encode(password_hashed).decode()
    account.password = base64_password_hashed
    account.password_salt = base64_salt
    db.session.commit()
    click.echo(click.style('Congratulations!, password has been reset.', fg='green'))


@click.command('reset-email', help='Reset the account email.')
@click.option('--email', prompt=True, help='The old email address of the account whose email you need to reset')
@click.option('--new-email', prompt=True, help='the new email.')
@click.option('--email-confirm', prompt=True, help='the new email confirm.')
def reset_email(email, new_email, email_confirm):
    if str(new_email).strip() != str(email_confirm).strip():
        click.echo(click.style('Sorry, new email and confirm email do not match.', fg='red'))
        return
    account = db.session.query(Account). \
        filter(Account.email == email). \
        one_or_none()
    if not account:
        click.echo(click.style('sorry. the account: [{}] not exist .'.format(email), fg='red'))
        return
    try:
        email_validate(new_email)
    except:
        click.echo(
            click.style('sorry. {} is not a valid email. '.format(email), fg='red'))
        return

    account.email = new_email
    db.session.commit()
    click.echo(click.style('Congratulations!, email has been reset.', fg='green'))


@click.command('generate-invitation-codes', help='Generate invitation codes.')
@click.option('--batch', help='The batch of invitation codes.')
@click.option('--count', prompt=True, help='Invitation codes count.')
def generate_invitation_codes(batch, count):
    if not batch:
        now = datetime.datetime.now()
        batch = now.strftime('%Y%m%d%H%M%S')

    if not count or int(count) <= 0:
        click.echo(click.style('sorry. the count must be greater than 0.', fg='red'))
        return

    count = int(count)

    click.echo('Start generate {} invitation codes for batch {}.'.format(count, batch))

    codes = ''
    for i in range(count):
        code = generate_invitation_code()
        invitation_code = InvitationCode(
            code=code,
            batch=batch
        )
        db.session.add(invitation_code)
        click.echo(code)

        codes += code + "\n"
    db.session.commit()

    filename = 'storage/invitation-codes-{}.txt'.format(batch)

    with open(filename, 'w') as f:
        f.write(codes)

    click.echo(click.style(
        'Congratulations! Generated {} invitation codes for batch {} and saved to the file \'{}\''.format(count, batch,
                                                                                                          filename),
        fg='green'))


def generate_invitation_code():
    code = generate_upper_string()
    while db.session.query(InvitationCode).filter(InvitationCode.code == code).count() > 0:
        code = generate_upper_string()

    return code


def generate_upper_string():
    letters_digits = string.ascii_uppercase + string.digits
    result = ""
    for i in range(8):
        result += random.choice(letters_digits)

    return result


@click.command('gen-recommended-apps', help='Number of records to generate')
def generate_recommended_apps():
    print('Generating recommended app data...')
    apps = App.query.all()
    for app in apps:
        recommended_app = RecommendedApp(
            app_id=app.id,
            description={
                'en': 'Description for ' + app.name,
                'zh': '描述 ' + app.name
            },
            copyright='Copyright ' + str(random.randint(1990, 2020)),
            privacy_policy='https://privacypolicy.example.com',
            category=random.choice(['Games', 'News', 'Music', 'Sports']),
            position=random.randint(1, 100),
            install_count=random.randint(100, 100000)
        )
        db.session.add(recommended_app)
    db.session.commit()
    print('Done!')


@click.command('sync-index', help='Sync vector objects to another vector store')
@click.option('--apply', is_flag=True, default=False,
              help='Apply index struct param to dataset.')
def sync_index_vector_objects(apply):
    print('Syncing vector objects...')
    datasets = db.session.query(Dataset).order_by(Dataset.created_at.asc()).limit(100).all()
    while len(datasets) > 0:
        latest_dataset = None
        for dataset in datasets:
            latest_dataset = dataset

            if dataset.indexing_technique != "high_quality":
                continue

            index_struct_dict = vector_store.to_index_struct(dataset.id)
            vector_index = VectorIndex(dataset=dataset, index_struct_dict=index_struct_dict)

            print('Syncing dataset {}...'.format(dataset.id))
            documents = db.session.query(Document).filter(Document.dataset_id == dataset.id).all()
            for document in documents:
                if document.indexing_status != 'completed' or document.archived or not document.enabled:
                    continue

                cache_key = 'synced_doc:{}'.format(document.id)
                cache_result = redis_client.get(cache_key)
                if cache_result is not None:
                    print('Document {} has been synced before, skip.'.format(document.id))
                    continue

                segments = db.session.query(DocumentSegment).filter(
                    DocumentSegment.document_id == document.id,
                    DocumentSegment.enabled == True
                ) \
                    .order_by(DocumentSegment.position.asc()).all()

                nodes = []
                previous_node = None
                for segment in segments:
                    relationships = {
                        DocumentRelationship.SOURCE: document.id
                    }

                    if previous_node:
                        relationships[DocumentRelationship.PREVIOUS] = previous_node.doc_id
                        previous_node.relationships[DocumentRelationship.NEXT] = segment.index_node_id

                    node = Node(
                        doc_id=segment.index_node_id,
                        doc_hash=segment.index_node_hash,
                        text=segment.content,
                        extra_info=None,
                        node_info=None,
                        relationships=relationships
                    )

                    previous_node = node

                    nodes.append(node)

                try:
                    vector_index.add_nodes(
                        nodes=nodes,
                        duplicate_check=True
                    )

                    redis_client.setex(cache_key, 86400, 1)
                except Exception:
                    logging.exception('failed to add nodes to vector index')
                    continue

            if apply:
                dataset.index_struct_dict = json.dumps(index_struct_dict)
                db.session.commit()

                print('Dataset {} index struct {} applied...'.format(dataset.id, index_struct_dict))

        if latest_dataset is None:
            datasets = []
        else:
            datasets = db.session.query(Dataset).filter(
                Dataset.created_at > latest_dataset.created_at,
                Dataset.id != latest_dataset.id
            ).order_by(Dataset.created_at.asc()).limit(100).all()

    print('Done!')


def register_commands(app):
    app.cli.add_command(reset_password)
    app.cli.add_command(reset_email)
    app.cli.add_command(generate_invitation_codes)
    app.cli.add_command(generate_recommended_apps)
    app.cli.add_command(sync_index_vector_objects)
