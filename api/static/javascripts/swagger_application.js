$(function() {
  loadSwagger();
});

var loadSwagger;
loadSwagger = function() {
  window.swaggerUi = new SwaggerUi({
    url: '/api/documentation/show',
    dom_id: 'swagger-ui-container',
    supportedSubmitMethods: ['get'],
    onComplete: function(swaggerApi, swaggerUi) {
      $('pre code').each(function(i, e) {
        hljs.highlightBlock(e);
      });
    },
    onFailure: function(data) {
      log('Unable to Load SwaggerUI');
    },
    docExpansion: 'none'
  });
  window.swaggerUi.load();
};
