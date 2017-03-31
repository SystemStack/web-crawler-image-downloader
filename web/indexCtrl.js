angular
.module("web-crawler",
  [
    "ngAnimate",
    "ngMaterial",
    "ngAria"
  ])
.controller("webCtrl", function ($scope, $window, $http) {
  $http.get('../cache_web/images.json')
       .then(function(res){
          $scope.images = res.data;
          console.log(res.data)
        });
});