$(document).ready(function()
{
	var ratebarOptions = 0;
	ratebarPresent = getRatebarPresent();
	setRatebar(ratebarPresent);
});
function getRatebarPresent()
{
	var present = 0;
	present = $("#ratebar").attr("_rate");//alert(present);
	return  present;
};
function setRatebar(present)
{
	$("#ratebar-box-orange").css("width",present+"%");
	$("#ratebar-box-present").text(present+"%");
	$("#ratebar-box-dot").css("left",present+"%");
	if(present>=50)
	{//alert(present);
		//var ll = $("#ratebar-box-line").width();alert(ll);
		var ol = $("#ratebar-box-orange").width();//alert(ol);
		var pl = $("#ratebar-box-present").width();//alert(pl);
		$("#ratebar-box-present").css("left",(ol-pl+10)+"px");
	}
	else
	{//alert(present);
		$("#ratebar-box-present").css("left",present+"%");
	};
};
