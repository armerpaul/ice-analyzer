var STATUS_LOADING = 'loading';
var MIN_QUERY_LENGTH = 3;

VueComponent('wtn-card', {
    props: ['card', 'remove'],
})

var app = VueApp({
    el: '#break-cost-table',
    data: {
        query: '',
        searchError: '',
        breakData: {},
        iceCodes: [],
        filters: {},
        cardsForTable: {},
        cards: {},
    },
    methods: {
        errorMessage: function(message) {
            console.error(message);
        },
        updateBreakCosts: function() {
            var self = this;

            var codes = _.keys(self.cardsForTable);
            var requestPromise = null;

            if (codes.length) {
                var params = {
                    'codes': codes
                };

                requestPromise = http.get('/api/break-costs/', params)
            }
            else {
                requestPromise = http.get('/api/break-costs/');
            }

            requestPromise.then(function(data) {
                self.iceCodes = _.keys(_.sample(data))
                self.breakData = data;
            });
        },
        searchForCardWithQuery: function(){
            var self = this;

            // TODO: Search cache first

            self.searchError = "";

            http.get('/api/cards/search/', { q: self.query }).then(function(card) {
                if (card) {
                    self.cards[card.code] = card;
                    self.cardsForTable[card.code] = self.cards[card.code];

                    self.query = "";
                    self.updateBreakCosts();    
                }
                else {
                    // ERROR
                    self.searchError = "There are no ice or breakers matching that query."
                }
            });
        },
        removeCard: function(card){
            var self = this;

            delete self.cardsForTable[card.code];
            self.updateBreakCosts();
        },
    },
    created: function() {
        var self = this;

        self.updateBreakCosts();
        http.get('/api/cards/default/').then(function(cards) {
            self.cards = cards;
            self.cardsForTable = self.cards;
        });
    } 
});