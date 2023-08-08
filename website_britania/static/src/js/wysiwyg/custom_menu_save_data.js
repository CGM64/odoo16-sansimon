odoo.define('website_britania.save_data_menu', (require) => {
    'use strict';
    let widgets = require('wysiwyg.widgets');

    widgets.LinkDialog.include({
        save: function() {
            let data = this._getData();
            if(data != null) {
                data.desplegable = this.$('input[name="desplegable"]').prop('checked') || false;
                data.tipo_submenu = this.$('input[name="tipo_submenu"]').prop('checked') || false;
                this.data.desplegable = data.desplegable;
                this.data.tipo_submenu = data.tipo_submenu;
            }
            return this._super.apply(this,arguments);
        }
    });
});