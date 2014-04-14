$(document).ready(function()
{
 var ratebarOptions = [];
 var oRates = $(".ratebar");//alert(oRates.length);
 oRates.each(function(){
  //ratebarOptions.push($(this).attr("_rate"));
  //alert($(this).attr("_rate"));
  setRatebar($(this), $(this).attr("_rate"));
    });
 
});
function setRatebar(obj, rate)
{
 $(obj).find(".ratebar-box-orange").css("width",rate+"%");
 $(obj).find(".ratebar-box-present").text(rate+"%");
 $(obj).find(".ratebar-box-dot").css("left",rate+"%");
 if(rate>=50)
 {//alert(present);
  //var ll = $("#ratebar-box-line").width();alert(ll);
  var ol = $(obj).find(".ratebar-box-orange").width();//alert(ol);
  var pl = $(obj).find(".ratebar-box-present").width();//alert(pl);
  $(obj).find(".ratebar-box-present").css("left",(ol-pl+10)+"px");
 }
 else
 {//alert(rate);
  $(obj).find(".ratebar-box-present").css("left",rate+"%");
 };
};