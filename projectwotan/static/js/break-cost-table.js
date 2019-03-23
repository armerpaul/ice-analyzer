var STATUS_LOADING = 'loading';

var app = new Vue({
    el: '#break-cost-table',
    data: {
      breakData: {},
      filters: {},
      cards: {
          
      }
    },
    methods: {
        errorMessage: function(message) {
            console.error(message);
        },
        updateBreakCosts: function() {
            var self = this;
            // I think people will often be search for specific breakers vs common ice 
            // or specific ice vs common breakers.
            // So maybe do /breakers|ice/list,of,card,codes/ and have it return a list 
            // of break costs sorted into lists of breakers|ice
            var params = {};
            var codes = Object.keys(self.cards);

            if (codes.length) {
                params.codes = codes;
            }

            http.get('/api/break-costs/', params).then(function(data) {
                self.breakData = data;
            });
        },
        addCardByCode: function(cardCode){
            this.cards[code] = STATUS_LOADING;
            // Start loading card data
        },
        removeCardByCode: function(cardCode){
            delete this.cards[code];
        },
    },
    created: function() {
        this.updateBreakCosts();
    } 
});