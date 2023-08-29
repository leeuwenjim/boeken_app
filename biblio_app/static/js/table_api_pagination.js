class ApiTable {
    constructor(endpoint, $table_body, columns, $navigation, $result_count) {
        this.endpoint = endpoint;
        this.$table_body = $table_body;
        this.columns = columns;
        this.$navigation = $navigation;
        this.filters = {};
        this.current_page = 1;
        this.$result_count = $result_count;
    }

    set_filter(key, value){
        if (value) {
            this.filters[key] = value;
        } else {
            this.remove_filter(key);
        }
    }

    remove_filter(key) {
        if (this.filters.hasOwnProperty(key)) delete this.filters[key]
    }


    set_navigation(navigation_data) {
        this.$navigation.html('');

        var $pagination_menu = $('<div>', {'class': 'ui pagination menu'});
        navigation_data.forEach((page_data) => {
            $pagination_menu.append(page_data['page']
                ?
                $('<a>', {'class': (this.current_page === page_data['page'] ? 'active item' : 'item')})
                    .text(page_data['page'].toString())
                    .on('click', () => {
                        this.load_page(page_data['page']);
                    })
                :
                $('<div>', {'class': 'disabled item'}).text('...'));
        });
        this.$navigation.append($pagination_menu)
    }

    row_data_to_row(row_data) {
        var $row = $('<tr>');
        for (var column_index in this.columns) {
            var content = this.columns[column_index](row_data);
            $row.append(
                $('<td>').append(content)
            );
            //$row.append('<td>').text(row_data[this.columns[column_index]])
        }
        return $row;
    }

    load_page(page_number) {
        this.$table_body.html('');

        var send_data = {
            'page': page_number
        };

        for (var key in this.filters) {
            if (key == 'page') continue;
            send_data[key] = this.filters[key];
        }

        $.get(this.endpoint, send_data, (data) =>{
            this.current_page = data['current'];
            data['results'].forEach((row_data) => {
                this.$table_body.append(this.row_data_to_row(row_data))
            });
            this.set_navigation(data['navigation']);
            this.$result_count.text(data['count']);
        }).fail(function() {
            const error_text = 'Er was een probleem met het laden van de data';
            if ($('#error_message_modal')) {
                $('#error_message_modal').find('content').text(error_text)
            } else {
                alert(error_text);
            }
        });

    }

}
