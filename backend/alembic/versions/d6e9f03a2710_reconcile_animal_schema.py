"""Reconcile animal and REMUM schema previously created outside Alembic.

Revision ID: d6e9f03a2710
Revises: c5a83b8d4563
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d6e9f03a2710"
down_revision = "c5a83b8d4563"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    enum_0 = postgresql.ENUM('ANTIRRABICA', 'CASTRACION', 'DESPARASITACION', 'OTRO', name='healtheventtype', create_type=False)
    enum_0.create(bind, checkfirst=True)
    enum_1 = postgresql.ENUM('A_SALVO', 'EXTRAVIADO', name='remumstatus', create_type=False)
    enum_1.create(bind, checkfirst=True)
    enum_2 = postgresql.ENUM('PERDIDO', 'ENCONTRADO', 'ALERTA_CEBO', 'EN_TRANSITO', 'ADOPCION', name='animalreporttype', create_type=False)
    enum_2.create(bind, checkfirst=True)
    enum_3 = postgresql.ENUM('PERRO', 'GATO', 'OTRO', name='pettype', create_type=False)
    enum_3.create(bind, checkfirst=True)
    enum_4 = postgresql.ENUM('SANO', 'LASTIMADO', 'SINTOMAS_ENVENENAMIENTO', 'CON_COLLAR', name='pethealthstatus', create_type=False)
    enum_4.create(bind, checkfirst=True)
    inspector = sa.inspect(bind)
    existing = {column["name"] for column in inspector.get_columns('categories')}
    if 'is_verified' not in existing:
        op.add_column('categories', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    if 'embedding_centroid' not in existing:
        op.add_column('categories', sa.Column('embedding_centroid', sa.Text(), nullable=True))
    if 'sample_count' not in existing:
        op.add_column('categories', sa.Column('sample_count', sa.Integer(), nullable=True, server_default=sa.text('1')))
    existing = {column["name"] for column in inspector.get_columns('reports')}
    if 'is_novel_category' not in existing:
        op.add_column('reports', sa.Column('is_novel_category', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    if 'embedding' not in existing:
        op.add_column('reports', sa.Column('embedding', sa.Text(), nullable=True))
    if 'report_type' not in existing:
        enum_2.create(bind, checkfirst=True)
        op.add_column('reports', sa.Column('report_type', enum_2, nullable=True, server_default=sa.text("'PERDIDO'")))
    if 'pet_type' not in existing:
        enum_3.create(bind, checkfirst=True)
        op.add_column('reports', sa.Column('pet_type', enum_3, nullable=True, server_default=sa.text("'PERRO'")))
    if 'pet_name' not in existing:
        op.add_column('reports', sa.Column('pet_name', sa.String(), nullable=True))
    if 'pet_breed' not in existing:
        op.add_column('reports', sa.Column('pet_breed', sa.String(), nullable=True))
    if 'color_description' not in existing:
        op.add_column('reports', sa.Column('color_description', sa.String(), nullable=True))
    if 'health_status' not in existing:
        enum_4.create(bind, checkfirst=True)
        op.add_column('reports', sa.Column('health_status', enum_4, nullable=True, server_default=sa.text("'SANO'")))
    if 'contact_name' not in existing:
        op.add_column('reports', sa.Column('contact_name', sa.String(), nullable=True))
    if 'contact_phone' not in existing:
        op.add_column('reports', sa.Column('contact_phone', sa.String(), nullable=True))
    if 'is_resolved' not in existing:
        op.add_column('reports', sa.Column('is_resolved', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    existing = {column["name"] for column in inspector.get_columns('feedback')}
    if 'used_for_retraining' not in existing:
        op.add_column('feedback', sa.Column('used_for_retraining', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    if not inspector.has_table('remum_records'):
        op.create_table('remum_records',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('pet_name', sa.String(), nullable=False),
            sa.Column('pet_type', enum_3, nullable=True),
            sa.Column('pet_breed', sa.String(), nullable=True),
            sa.Column('color_description', sa.String(), nullable=True),
            sa.Column('image_path', sa.String(), nullable=True),
            sa.Column('chip_number', sa.String(), nullable=True),
            sa.Column('qr_code_id', sa.String(), nullable=False),
            sa.Column('is_community_pet', sa.Boolean(), nullable=True),
            sa.Column('status', enum_1, nullable=True),
            sa.Column('address', sa.String(), nullable=True),
            sa.Column('latitude', sa.Float(), nullable=True),
            sa.Column('longitude', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index('ix_remum_records_id', 'remum_records', ['id'], unique=False)
        op.create_index('ix_remum_records_qr_code_id', 'remum_records', ['qr_code_id'], unique=True)
    if not inspector.has_table('remum_health_events'):
        op.create_table('remum_health_events',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('remum_record_id', sa.Integer(), sa.ForeignKey('remum_records.id'), nullable=False),
            sa.Column('event_type', enum_0, nullable=False),
            sa.Column('date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('certificate_number', sa.String(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
        )
        op.create_index('ix_remum_health_events_id', 'remum_health_events', ['id'], unique=False)
    if not inspector.has_table('remum_godparents'):
        op.create_table('remum_godparents',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('remum_record_id', sa.Integer(), sa.ForeignKey('remum_records.id'), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('task', sa.String(), nullable=False),
        )
        op.create_index('ix_remum_godparents_id', 'remum_godparents', ['id'], unique=False)


def downgrade():
    raise RuntimeError("Reconciliación de esquema histórico: restaurar un backup para revertir sin eliminar datos preexistentes")
