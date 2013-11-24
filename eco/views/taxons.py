# encoding: utf-8

import json
import transaction
import itertools

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound


from eco.models import (
    DBSession,
    Cards,
    Taxon, Synonym, TAXON_TYPES, TAXON_ALL_QUERY, TAXON_ID_QUERY
)

from eco.models import MAMMALIA, AVES, PLANTAE, ARA, ARTHROPODA, MOSS, LICHENES
import helpers

@view_config(route_name='taxon_tree', renderer='json')
def tree_root(request):
    path_name = 'path' if 'path' in request.params else 'basePath'
    hierarchical_path = request.params[path_name].replace('"', '')

    if hierarchical_path == '.':
        parent_id = None
    else:
        parent_id = int(str.split(str(hierarchical_path), '/')[-1])

    dbsession = DBSession()
    parent_taxon = dbsession.query(Taxon).filter_by(id = parent_id).first()
    children_taxons = dbsession.query(Taxon).filter_by(parent_id = parent_id)
    dbsession.flush()

    if hierarchical_path == '.':
        block = {
            'name': '.',
            'path': hierarchical_path,
            'directory': True,
            'total': 1,
            'status': 200,
            'items': [{
                'name': '.',
                'id': -1,
                'path': hierarchical_path,
                'directory': True
            }]
        }
    else:
        block = {
            'name': parent_taxon.name,
            'path': hierarchical_path,
            'directory': True,
            'total': 1,
            'status': 200,
            'items': []
        }

    children_taxons_json = []
    for taxon in children_taxons:
        children_taxons_json.append(_taxon_to_node(hierarchical_path, taxon))

    if hierarchical_path == '.':
        block['items'][0]['children'] = children_taxons_json
    else:
        block['items'] = children_taxons_json

    return block if block else children_taxons_json


def _taxon_to_node(path, taxon):
    node = {
        'id': taxon.id,
        'path': path + '/' + str(taxon.id),
        'name': taxon.name
    }

    if taxon.is_last_taxon():
        node['is_specie'] = True
    else:
        node['directory'] = True
    if taxon.author:
        node['author'] = taxon.author
    return node

# Отдать прямые потомки таксона в виде, пригодном для использования в Ext.treepanel:
@view_config(route_name='taxon_direct_child', renderer='json')
def direct_child(request):
    
    # Ext посылает запрос, содержащий строку вида 'node'='taxon_идентификатор')
    # например, 'node'='taxon_1', где id = id записи в таблице taxons
    # (об идентификаторах см. ниже, в цикле,
    # где в ответ на запрос выдаются дочерние узлы с идентификаторами)

    # Два граничных случая:
    # taxon == 'root': Корень дерева таксонов, childern=все записи из Kingdom
    # taxon.is_last_taxon == True: конец иерархии (это последний таксон) => leaf:=True
    node = request.params['node']

    dbsession = DBSession()
    try:
        if node == 'root':
            childern = dbsession.query(Taxon).filter_by(parent_id = None).all()
        else:
            node = node.split('_')
            id = int(node[1])
            childern = dbsession.query(Taxon).filter_by(parent_id=id).all()
                
    except NoResultFound:
        return {'success': False, 'msg': 'Результатов, соответствующих запросу, не найдено'}

    # Генерируем описания узлов для Ext.treepanel
    rows = []
    for taxon in childern:
        node = {}
        # Ext хочет получать информацию из поля 'text'
        # Сформируем это поле из названия и автора
        author = taxon.author if taxon.author else ''
        is_last = taxon.is_last_taxon()
        
        node['id']   = 'taxon_' + str(taxon.id)
        node['leaf'] = is_last
        if is_last:
            node['text'] = "<b>%s</b> %s" % (taxon.name , author) 
        else:
            node['text'] = "%s %s" % (taxon.name , author)
        rows.append(node)
    return rows




# Выдать данные из таблиц taxon,synonym в формате json согласно фильтру
@view_config(route_name='taxon_filter', renderer='json')
def taxon_filter(request):
    dbsession = DBSession()
    
    query_str = request.params['name']
    start = int(request.params['start'])
    count = int(request.params['count'])

    # Нужно выдернуть номера id, названия таксонов и авторов (для синонимов) из таблиц таксонов и синонимов
    try:
        # ищем в таблице таксонов:
        aFilter = "UPPER(%s) LIKE '%s%s%s'" % ('name', '%', query_str.upper(),'%')
        tax_all = dbsession.query(Taxon.id, Taxon.name, Taxon.author).filter(aFilter).all()
        
        # ищем в таблице синонимов:
        aFilter = "UPPER(%s) LIKE '%s%s%s'" % ('synonym', '%', query_str.upper(),'%')
        s_all = dbsession.query(Synonym.species_id, Synonym.synonym, Synonym.author).filter(aFilter).all()
        
        all = [tax_all + s_all][0]
        itemsPage = all[start:start+count]
    except DBAPIError:
        return {'success': False, 'msg': 'Ошибка подключения к БД'}
    rows = []
    if all:
        rec_id = itertools.count()
        rows = [{'recId': rec_id.next(), 'id': id, 'name': name, 'author': author} for id, name, author in itemsPage]
    return {'items': rows, 'success': True, 'numRows': len(all), 'identity': 'id'}

# Выдать данные из таблиц taxon,synonym в формате json согласно фильтру
@view_config(route_name='species_filter', renderer='json')
def species_filter(request):
    dbsession = DBSession()
    try: 
        query_str = request.params['taxon']
    except KeyError:
        query_str = ''
    taxon_id = request.matchdict['id']
    taxon_type = request.matchdict['type']

    species_types = {'mammalia': MAMMALIA, 'aves': AVES, 'plantae': PLANTAE, 'ara': ARA, 
        'arthropoda': ARTHROPODA, 'moss': MOSS, 'lichenes': LICHENES}
    try:
        sp = species_types[taxon_type]
    except KeyError:
        return {'success': False, 'msg': 'Неверный вид организма'}
    
    success = True
    try:
        # Если id известен, выберем запись:
        if taxon_id:
            known_tax = dbsession.query(Taxon.id, Taxon.name, Taxon.author, Taxon.source).filter(Taxon.id == taxon_id).all()
        else:
            known_tax = []
        
        # Если пришла строка запроса, обработаем:
        all_t, all_s = [], []
        if query_str or query_str == '':
            target = dbsession.query(Taxon).filter(Taxon.name.in_(sp)).all()
            target_ids = [t.id for t in target]
            target_ids = ", ".join([str(num) for num in target_ids])
            
            # Найдем таксоны заданного типа организмов с названием, удовл. шаблону:
            qs = TAXON_ALL_QUERY  % (target_ids, TAXON_TYPES[len(TAXON_TYPES)-1])
            subquery = " AND UPPER(%s) LIKE '%s%s%s'" % ('name', '%', query_str.upper(),'%')
            qs = qs + subquery + ';'
            all_t = dbsession.query(Taxon.id, Taxon.name, Taxon.author, Taxon.source).from_statement(qs).all()
            
            # Синонимы
            subquery = TAXON_ID_QUERY % (target_ids, TAXON_TYPES[len(TAXON_TYPES)-1])
            qsyn = '''
            SELECT * FROM synonym
            WHERE
              UPPER(%s) LIKE '%s%s%s' AND species_id IN ( %s);
            '''  % ('synonym', '%', query_str.upper(),'%', subquery)
            all_s = dbsession.query(Synonym.species_id, Synonym.synonym, Synonym.author, Synonym.source).from_statement(qsyn).all()
        
    except DBAPIError:
        success = False
    
    taxons = known_tax + all_t + all_s
    numRows = len(taxons)

    start, count = helpers.get_paging_params(request.params)
    if start and count:
        taxons = taxons[start:start + count]

    taxons_json = []
    if taxons:
        taxons_json = [{'id': id, 'name': name} for id, name, author, source in taxons]

    return {
        'items': taxons_json,
        'success': success,
        'numRows': numRows,
        'identity': 'id'
    }


@view_config(route_name='taxon_parent_path', renderer='json')
def parent_path(request):
    taxon_id = request.matchdict['id']
    
    taxons = Taxon.parent_taxons(taxon_id)
    path = [t.id for t in taxons]
    
    return {'success': True, 'path': path}

# Выборка видов из БД
@view_config(route_name='species_name', renderer='json')
def species_name(request):
    dbsession = DBSession()
    species_types = {'mammalia': MAMMALIA, 'aves': AVES, 'plantae': PLANTAE, 'ara': ARA, 
        'arthropoda': ARTHROPODA, 'moss': MOSS, 'lichenes': LICHENES}
    rows = []
    rec_id = itertools.count()
    try:
        for sp in species_types.keys():
            slist = species_types[sp]
            target = dbsession.query(Taxon).filter(Taxon.name.in_(slist)).all()
            target_ids = [t.id for t in target]
            tax_all = Taxon.species_by_taxon(target_ids)            
            rows = rows + [
                {   'recId':    rec_id.next(),
                    'id':       row['id'], 
                    'name':     row['name'], 
                    'author':   row['author'], 
                    'source':   row['source'], 
                    'organism': sp, 'synonim': False
                } 
            for  row in tax_all]
            # соберем синонимы:
            syn = dbsession.query(Synonym.species_id, Synonym.synonym, Synonym.author, Synonym.source).filter(Synonym.species_id.in_([row['id'] for row in tax_all])).all()
            rows = rows + [
                {   'recId':    rec_id.next(),
                    'id':       row[0], 
                    'name':     row[1], 
                    'author':   row[2], 
                    'source':   row[3], 
                    'organism': sp, 'synonim': True
                } 
            for  row in syn]
    except DBAPIError:
        result = {'success': False, 'msg': 'Ошибка подключения к БД'}

    return {'data': rows, 'success': True, 'totalCount': len(rows)}

# тип таксона по его id
@view_config(route_name='taxon_type', renderer='json')
def taxon_type(request):
    taxon_id = request.matchdict['id']
    
    dbsession = DBSession()
    p = dbsession.query(Taxon).filter(Taxon.id == taxon_id).one()

    types = {'mammalia': p.is_mammalia(), 'aves': p.is_aves(), 'plantae': p.is_plantae(), 'ara': p.is_ara(), 
        'arthropoda': p.is_arthropoda(), 'moss': p.is_moss(), 'lichenes': p.is_lichenes()}
    
    return types

    


