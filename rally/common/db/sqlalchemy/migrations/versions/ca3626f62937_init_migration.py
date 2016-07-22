# Copyright (c) 2016 Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


"""Init migration

Revision ID: ca3626f62937
Revises:
Create Date: 2016-01-07 00:27:39.687814

"""

# revision identifiers, used by Alembic.
revision = "ca3626f62937"
down_revision = None
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

import rally
from rally.common.db.sqlalchemy import api
from rally import exceptions


def upgrade():
    dialect = api.get_engine().dialect

    deployments_columns = [
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("parent_uuid", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "config",
            rally.common.db.sqlalchemy.types.MutableJSONEncodedDict(),
            nullable=False),
        sa.Column("admin", sa.PickleType(), nullable=True),
        sa.Column("users", sa.PickleType(), nullable=False),
        sa.Column("enum_deployments_status", sa.Enum(
            "cleanup->failed", "cleanup->finished", "cleanup->started",
            "deploy->failed", "deploy->finished", "deploy->inconsistent",
            "deploy->init", "deploy->started", "deploy->subdeploy",
            name="enum_deploy_status"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    ]

    if dialect.name.startswith("sqlite"):
        deployments_columns.append(
            sa.ForeignKeyConstraint(
                ["parent_uuid"], [u"deployments.uuid"],
                name="fk_parent_uuid", use_alter=True)
        )

    # commands auto generated by Alembic - please adjust!
    op.create_table("deployments", *deployments_columns)

    op.create_index("deployment_parent_uuid", "deployments",
                    ["parent_uuid"], unique=False)

    op.create_index("deployment_uuid", "deployments", ["uuid"], unique=True)

    if not dialect.name.startswith("sqlite"):
        op.create_foreign_key("fk_parent_uuid", "deployments", "deployments",
                              ["parent_uuid"], ["uuid"])

    op.create_table(
        "workers",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hostname", name="uniq_worker@hostname")
    )

    op.create_table(
        "resources",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column(
            "info",
            rally.common.db.sqlalchemy.types.MutableJSONEncodedDict(),
            nullable=False),
        sa.Column("deployment_uuid", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["deployment_uuid"], [u"deployments.uuid"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("resource_deployment_uuid", "resources",
                    ["deployment_uuid"], unique=False)

    op.create_index("resource_provider_name", "resources",
                    ["deployment_uuid", "provider_name"], unique=False)

    op.create_index("resource_provider_name_and_type", "resources",
                    ["deployment_uuid", "provider_name", "type"],
                    unique=False)

    op.create_index("resource_type", "resources",
                    ["deployment_uuid", "type"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("status", sa.Enum(
            "aborted", "aborting", "cleaning up", "failed", "finished",
            "init", "paused", "running", "setting up", "soft_aborting",
            "verifying", name="enum_tasks_status"), nullable=False),
        sa.Column("verification_log", sa.Text(), nullable=True),
        sa.Column("tag", sa.String(length=64), nullable=True),
        sa.Column("deployment_uuid", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["deployment_uuid"], [u"deployments.uuid"], ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index("task_deployment", "tasks", ["deployment_uuid"],
                    unique=False)

    op.create_index("task_status", "tasks", ["status"], unique=False)

    op.create_index("task_uuid", "tasks", ["uuid"], unique=True)

    op.create_table(
        "verifications",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("deployment_uuid", sa.String(length=36), nullable=False),
        sa.Column("status", sa.Enum(
            "aborted", "aborting", "cleaning up", "failed", "finished",
            "init", "paused", "running", "setting up", "soft_aborting",
            "verifying", name="enum_tasks_status"), nullable=False),
        sa.Column("set_name", sa.String(length=20), nullable=True),
        sa.Column("tests", sa.Integer(), nullable=True),
        sa.Column("errors", sa.Integer(), nullable=True),
        sa.Column("failures", sa.Integer(), nullable=True),
        sa.Column("time", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["deployment_uuid"], [u"deployments.uuid"], ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index("verification_uuid", "verifications", ["uuid"],
                    unique=True)

    op.create_table(
        "task_results",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            rally.common.db.sqlalchemy.types.MutableJSONEncodedDict(),
            nullable=False),
        sa.Column(
            "data",
            rally.common.db.sqlalchemy.types.BigMutableJSONEncodedDict(),
            nullable=False),
        sa.Column("task_uuid", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["task_uuid"], ["tasks.uuid"], ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_table(
        "verification_results",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("verification_uuid", sa.String(length=36), nullable=True),
        sa.Column(
            "data",
            rally.common.db.sqlalchemy.types.BigMutableJSONEncodedDict(),
            nullable=False),
        sa.ForeignKeyConstraint(["verification_uuid"], ["verifications.uuid"]),
        sa.PrimaryKeyConstraint("id")
    )
    # end Alembic commands


def downgrade():
    raise exceptions.DowngradeNotSupported()
