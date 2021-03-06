define([
    'dojo/_base/declare',
    'dojo/_base/lang',
    'dojo/topic',
    'dojo/dom',
    'dojo/on',
    'dojo/dom-attr',
    'dojo/_base/array',
    'dijit/_WidgetBase',
    'dijit/_TemplatedMixin'
], function (declare, lang, topic, dom, on, domAttr, array, _WidgetBase,
             _TemplatedMixin) {
    return declare([_WidgetBase, _TemplatedMixin], {
        templateString: '<div></div>',

        postCreate: function (kwArgs) {
            this.filterForm = dom.byId('formFilter');
            this.searchBtn = dom.byId('search');

            $(this.domNode).jtable({
                title: 'Таблица карточек',
                paging: true,
                sorting: true,
                defaultSorting: 'taxon_name ASC',
                actions: {
                    listAction: application_root + '/cards/manager/jtable/list'
                },
                fields: {
                    person__id: {
                        key: true,
                        list: false
                    },
                    taxon__name: {
                        title: 'Латинское название',
                        width: '16%'
                    },
                    inserter__name: {
                        title: 'Вносил',
                        width: '16%'
                    },
                    observer__name: {
                        title: 'Наблюдал',
                        width: '16%'
                    },
                    cards__added_date: {
                        title: 'Дата внесения',
                        width: '16%',
                        type: 'date',
                        displayFormat: 'dd.mm.yy'
                    },
                    cards__observed_date: {
                        title: 'Дата наблюдения',
                        width: '16%',
                        type: 'date',
                        displayFormat: 'dd.mm.yy'
                    }
                }
            });

            $(this.domNode).jtable('load');
            this._filterElements = $(this.filterForm).find('[data-filter-item]');

            this._buildDatePickers();
            this._bindExportControls();

            on(this.searchBtn, 'click', lang.hitch(this, function (e) {
                e.preventDefault();
                this.filterTable();
            }));
        },

        _buildDatePickers: function () {
            $('input[data-datepicker]').datepicker({
                dateFormat: 'dd.mm.yy'
            });
        },

        _bindExportControls: function () {
            var $formTemporary = $('#formTemporary');

            $('#formExport input').each(lang.hitch(this, function (i, input) {
                var $input = $(input),
                    fileType = $input.attr('data-file-type');

                $input.click(lang.hitch(this, function () {
                    var filter = this._getFilter();
                    $.each(filter, function (k, v) {
                        $formTemporary.append('<input type="hidden" name="' + k + '" value="' + v + '" />');
                    });
                    $formTemporary.attr('action', application_root + '/export/cards/?format=' + fileType);
                    $formTemporary.submit();
                }));
            }))
        },

        _getFilter: function () {
            var filter = {};
            $.each(this._filterElements, function (i, filterElement) {
                var $filterElement = $(filterElement);
                var value = $filterElement.val();
                if (value) {
                    filter[$filterElement.attr('id')] = value;
                }
            });
            return filter;
        },

        _filterElements: null,
        filterTable: function () {
            $(this.domNode).jtable('load', this._getFilter());
        }
    });
});