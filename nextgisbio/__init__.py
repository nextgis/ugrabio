# encoding: utf-8

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig


from nextgisbio.models import DBSession
from nextgisbio.security import RootFactory, groupfinder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    my_session_factory = UnencryptedCookieSessionFactoryConfig('sosecret')
    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory=my_session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
    )
    config.include('pyramid_mako')

    config.add_static_view('static', 'nextgisbio:static', cache_max_age=3600)
    config.add_static_view('contrib', 'nextgisbio:contrib', cache_max_age=3600)

    config.add_route('home', '/', factory=RootFactory)
    config.add_route('taxons_editor', '/taxons/editor', factory=RootFactory)

    config.add_route('login', '/login', factory=RootFactory)
    config.add_route('logout', '/logout', factory=RootFactory)

    config.add_route('taxon_filter', '/taxon/filter', factory=RootFactory)
    config.add_route('species_name', '/species', factory=RootFactory)
    config.add_route('taxon_direct_child', '/taxon/direct_child',      factory=RootFactory)
    config.add_route('get_taxon_path', '/taxon/path/{id}',  factory=RootFactory)
    config.add_route('taxon_type', '/taxon/type/{id}',       factory=RootFactory)
    config.add_route('taxon_cbtree', '/cbtree/taxons', factory=RootFactory)
    config.add_route('get_taxon_tree_childrens', '/tree/taxons/{taxon_parent_id}', factory=RootFactory)
    config.add_route('taxon_tree', '/tree/taxons/', factory=RootFactory)
    config.add_route('get_child_taxons_by_parent', '/taxon/child', factory=RootFactory)
    config.add_route('get_taxon', '/taxon/{id}', factory=RootFactory)

    config.add_route('get_synonyms', 'taxons/synonyms/{taxon_id}/', factory=RootFactory)
    config.add_route('synonyms_by_taxon', 'taxons/synonyms/{taxon_id}/{synonym_id}', factory=RootFactory)

    # reports
    config.add_route('protected_species_list', '/reports/protected_species_list', factory=RootFactory)
    config.add_route('redbook_filter', '/redbook/filter', factory=RootFactory)
    config.add_route('species_by_redbook', '/species/redbook/{redbook_id}', factory=RootFactory)

    # Фильтр видов по его типу, подстроки названия и (если указан) id
    config.add_route('species_filter',    '/species/{type}/{id:[0-9]*}',       factory=RootFactory)

    # Карточки наблюдений, где был описан определенный таксон:
    config.add_route('points_text',         '/points_text/',            factory=RootFactory)

    # Экспорт карточек наблюдений
    config.add_route('cards_download',  '/cards_download/{format}/',    factory=RootFactory)
    # Создание новой карточки наблюдения 
    config.add_route('new_card',            '/cards/new',               factory=RootFactory)
    # Сохранить карточку после редактирования
    config.add_route('save_card',           '/cards/save',         factory=RootFactory)
    # Карточка наблюдений в формате json
    config.add_route('cards_view',          '/cards/{id}',              factory=RootFactory)

    config.add_route('card',          '/card/{id}',              factory=RootFactory)

    config.add_route('get_card_images', '/card/{id}/images', factory=RootFactory)

    # Аннотированные списки в квадрате № id, с описанем определенного таксона:
    config.add_route('anns_text',         '/anns_text/square/{id}',     factory=RootFactory)
    # Экспорт аннотированных списков
    config.add_route('anns_download',  '/anns_download/{format}/',      factory=RootFactory)
    # Создание нового анн. списка
    config.add_route('new_anlist',          '/annotation/new',          factory=RootFactory)
    # Сохранить анн. список после редактирования
    config.add_route('save_anlist',         '/annotation/save',    factory=RootFactory)

    config.add_route('annotation',         '/annotation/{id}',    factory=RootFactory)

    # Квадраты и ключевые участки
    config.add_route('squares_text',        '/squares_text/',           factory=RootFactory)
    # Квадрат и ключевые участки, на которые он попадает
    config.add_route('square',              '/square/{id}',             factory=RootFactory)
    # Аннотации по ключевому участку
    config.add_route('karea_ann',           '/key_area/{id}/ann',       factory=RootFactory)

    # Квадраты, где был найден определенный таксон:
    config.add_route('areal_text',          '/areal_text/',             factory=RootFactory)
    # Квадраты, где был найден определенный таксон:
    config.add_route('areal_download',      '/areal/download/',         factory=RootFactory)

    # Выдать данные из таблицы связей квадраты-КУ в формате csv
    config.add_route('s_ka_association_download',  'association_download',       factory=RootFactory)

    config.add_route('upload_image', '/images/upload/{type}/{id}', factory=RootFactory)
    config.add_route('remove_image', '/images/remove/{type}/{image_id}', factory=RootFactory)

    config.add_route('cards_table', '/cards/table/', factory=RootFactory)
    config.add_route('cards_jtable_browse', '/cards/manager/jtable/list', factory=RootFactory)
    config.add_route('cards_by_user', '/reports/cards_by_user/', factory=RootFactory)
    config.add_route('cards_by_user_jtable_browse', '/reports/cards_by_user/jtable/list', factory=RootFactory)

    config.add_route('export_cards_table', '/export/cards/', factory=RootFactory)

    config.add_route('persons_manager', '/persons/manager', factory=RootFactory)
    config.add_route('persons_jtable_browse', '/persons/manager/jtable/list', factory=RootFactory)
    config.add_route('persons_jtable_save', '/persons/manager/jtable/save', factory=RootFactory)
    config.add_route('persons_jtable_delete', '/persons/manager/jtable/delete', factory=RootFactory)
    config.add_route('persons_get_users_options', '/persons/manager/options/users', factory=RootFactory)

    config.add_route('get_users', '/users/', factory=RootFactory)

    # Справочники:
    config.add_route('person_name',         '/person_name',             factory=RootFactory)
    # Инфоресурсы
    config.add_route('inforesources_name',  'inforesources_name',       factory=RootFactory)

    # jtable specific views
    config.add_route('table_browse_jtable', '{table}/jtable', factory=RootFactory)
    config.add_route('table_save_jtable', '{table}/jtable/save', factory=RootFactory)
    config.add_route('table_delete_jtable', '{table}/jtable/delete', factory=RootFactory)

    # Выдать данные из таблицы в формате json
    config.add_route('table_browse',        '{table}_browse',           factory=RootFactory)

    # Выдать данные по конкретной записи из таблицы в формате json:
    config.add_route('table_view',          '/{table}/{id}',            factory=RootFactory)

    # Выдать данные из таблицы в формате csv
    config.add_route('table_download',        '{table}_download',       factory=RootFactory)

    config.scan()

    return config.make_wsgi_app()
