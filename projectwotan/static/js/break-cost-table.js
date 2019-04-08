var STATUS_LOADING = 'loading';
var MIN_QUERY_LENGTH = 3;

VueComponent('ia-card', {
    props: ['card', 'index', 'remove'],
    computed: {
        cssClasses: function() {
            var cssClasses = [ this.card.type ];

            // Class for original layout
            if (!this.card.isNisei) {
                cssClasses.push('--old-layout');            
            }

            return cssClasses;
        },
        stats: function() {
            var stats = [];
            var addStat = function(cssClass, value) {
                stats.push({
                    'cssClass': cssClass,
                    'value': value
                });
            }

            addStat('--strength', this.card.strength);

            if ('ice' === this.card.type) {
                addStat('icon icon-subroutine', this.card.subroutines.length);
    
            }

            return stats;
        }
    }
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
        isHoverFrozen: false,
        hover: {
            ice: -1,
            breaker: -1
        }
    },
    methods: {
        errorMessage: function(message) {
            console.error(message);
        },
        toggleHoverFreeze: function() {
            this.isHoverFrozen = !this.isHoverFrozen;
        },
        setHover: function(iceCode, breakerCode) {
            if (!this.isHoverFrozen) {
                this.hover.ice = iceCode;
                this.hover.breaker = breakerCode;    
            }
        },
        cellCssClasses: function(iceCode, breakerCode) {
            var matchesRow = breakerCode && this.hover.breaker === breakerCode;
            var matchesCol = iceCode && this.hover.ice === iceCode;
            var isHover = matchesRow || matchesCol
            return {
                '--hover': isHover,
                '--hover-column': matchesCol,
                '--hover-row': matchesRow,
                '--hover-target': matchesRow && matchesCol,
                '--frozen': this.isHoverFrozen && isHover
            };
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