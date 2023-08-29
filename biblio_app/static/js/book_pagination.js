class BookPagination {
    constructor(endpoint, $card_container, $navigation_container, show_publisher) {
        this.endpoint = endpoint;
        this.card_container = $card_container;
        this.navigation_container = $navigation_container;
        this.current_page = 1;
        this.show_publisher = show_publisher;
        this.filters = {}
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

    format_authors(authors_data) {
        var result = $('<div>', {'class': 'description'});
        authors_data.forEach((author) => {
            result.append(
                $('<a>', {'href': '/authors/' + author['id'] + '/'}).text(author['first_name'] + ' ' + author['last_name']), ' '
            );
        });
        return result;
    }

    set_navigation(navigation_data) {
        this.navigation_container.html('');

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
        this.navigation_container.append($pagination_menu)
    }

    data_to_card(data) {
        return $('<div>', {'class': 'card'}).append(
            $('<div>', {'class': 'image'}).append(
                $('<img>', {'class': 'card_image', 'src': (data['cover'] ? data['cover'] : '/static/img/book-placeholder.jpg')})
            ),
            $('<div>', {'class': 'content'}).append(
                $('<div>', {'class': 'header'}).css('cursor', 'pointer').text(data['title']).on('click', () => {
                    location.href="/books/"+data['id']+"/"
                }),
                $('<div>', {'class': 'meta'}).text(data['original_title'] ? data['original_title'] : ' '),
                this.format_authors(data['authors'])
            ),
            (this.show_publisher ? $('<div>', {'class': 'extra content'}).append(
                (data['publisher'] ? $('<span>').text(data['publisher']['name']).css('cursor', 'pointer').on('click', function() {location.href="/publishers/"+data['publisher']['id']+"/"}) : $()),
                (data['publish_year'] ? ' (' + data['publish_year'].toString() + ')' : '')
            ) : $())
        );
    }

    load_page(page_number) {
        this.card_container.html('');

        var send_data = {
            'page': page_number
        };

        for (var key in this.filters) {
            if (key == 'page') continue;
            send_data[key] = this.filters[key];
        }

        $.get(this.endpoint, send_data, (data) =>{
            this.current_page = data['current'];
            data['results'].forEach((book_data) => {
                this.card_container.append(this.data_to_card(book_data));
            });
            this.set_navigation(data['navigation'])
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
