window.onload = function()
{
	bindAll();
};

var searchObj = {};//district base type level
searchObj.district = [];
searchObj.base = [];
searchObj.type = [];
searchObj.level = [];
matchObj = {};
matchObj.aObj = [];
matchObj.index = 0;

function bindAll()
{
	var base = document.getElementById('base').children;
	var level = document.getElementById('level').children;
	var subjects = document.getElementById('subjects').children;
		
	for(var i=0;i<level.length;i++)
	{
		level[i].index = i;
		level[i].onclick = function()
		{
			if(this.index=='0')
			{
				if(this.className=='live') for(var i=0;i<level.length;i++) level[i].className='death';
				else for(var i=0;i<level.length;i++) level[i].className='live';
			}
			else
			{
				if(level[0].className=='live')
				{
					for(var i=0;i<level.length;i++) level[i].className='death';
					this.className='live';
				}
				else
				{
					if(this.className==='live')this.className='death';
					else this.className='live';			
				};
							
			};
			checkClickedObj('level');
			refreshFall();
		}
	};
	
	for(var i=0;i<subjects.length;i++)
	{
		subjects[i].index = i;
		subjects[i].onclick = function()
		{
			if(this.index=='0')
			{
				if(this.className=='live') for(var i=0;i<subjects.length;i++) subjects[i].className='death';
				else for(var i=0;i<subjects.length;i++) subjects[i].className='live';
			}
			else
			{
				if(subjects[0].className=='live')
				{
					for(var i=0;i<subjects.length;i++) subjects[i].className='death';
					this.className='live';
				}
				else
				{
					if(this.className==='live')this.className='death';
					else this.className='live';			
				};
							
			};
			checkClickedObj('subjects');
			refreshFall();
		}
	};	
	
};
function creatLi(arr)
{
	if(matchObj.index===matchObj.aObj.length)
	{
		//alert("已无符合要求的数据 ！");
		return;
	};
	//var _arr = {};_arr = arr;
	var oLi=document.createElement('li');
   
	//oLi.style.height=rnd(200,400)+'px';	
	//oLi.style.background='rgb('+rnd(0,255)+','+rnd(0,255)+','+rnd(0,255)+')';

	//var course = rnd(0,9), tu = rnd(0,13);
	//var collegeName = getCollegeName(rnd(0,10)), courseName = getCourseName(rnd(0,10));
	//alert(matchObj.aObj );
	
	//var like = rnd(99,999), learn = rnd(99,9999), fee = rnd(9,999);if(fee<400)fee="免费";
	var courseName = matchObj.aObj[matchObj.index].name, collegeName = matchObj.aObj[matchObj.index].org,tu = matchObj.aObj[matchObj.index].logo;
	var vurl=matchObj.aObj[matchObj.index].logo;
	
	var idstr = matchObj.aObj[matchObj.index].id;
	//alert(idstr);
	idstr=idstr.replace(/[.]/g,"/");
	//alert(tu);
	tu="http://"+tu;
	idstr="http://mooc.xiaodun.cn/courses/"+idstr+"/about";
	//http://mooc.xiaodun.cn/courses/hackervip/vbs001/2014_T1/about
	
	//alert(1);
	/*
	oLi.innerHTML = "\<div class='fall\-li'\>" + 
						"\<div class='nav\-img'><img width=270  style=\"width:270px;\" src\='" + tu + "' onclick=\"goinfo('"+idstr+"')\"\/><\/div>" +
						"\<div class='nav\-menu\'\>\<strong\><a href='"+idstr+"'>"+courseName+"</a>\<\/strong\>\<br \/\>\<span\>"+collegeName+"</span></div>" +
						"\<div class\='nav\-detail'\>" +
						"\</div\>" +
					"\<\/div>";
	*/
	
	oLi.innerHTML = "" + 
	"<div class='courses-listing-item'>" +
				"<article class='course' id='hackervip/ARP001/2014_T1'>" +
				"<a href='"+idstr+"'>" +
					"<div class='inner-wrapper'>" +
						"<header class='course-preview'>" +
							"<hgroup>" +
								"<h2><span class='course-number'>ARP001<\/span> "+courseName+"<\/h2>" +
							"<\/hgroup>" +
							"<div class='info-link'><span>➔</span></div>" +
						"<\/header>" +
						"<section class='info'>" +
							"<div class='cover-image'>" +
								"<img alt='ARP001 ARP欺骗与防范 Cover Image' src='"+tu+"'>" +
							"<\/div>" +
							"<div class='desc'>" +
								"<p>" +"由于局域网的网络流通不是根据IP地址进行，而是按照MAC地址进行传输。所以，那个伪造出来的MAC地址在A上被改变成一个不存在的MAC地址，这样就会造成网络不通，导致A不能Ping通C！这就是一个简单的ARP欺骗。<\/p>" +
							"<\/div>" +
							"<div class='bottom'>" +
								"<span class='university'>"+collegeName+"<\/span>" +
								"<span class='start-date'>3, 22, 2014<\/span>" +
							"<\/div>" +
						"<\/section>" +
					"<\/div>" +
					"<div class='meta-info'>" +
						"<p class='university'>hackervip</p>" +
					"<\/div>" +
				"<\/a>" +
				"<\/article>" +
			"<\/div>" +
		"";
	matchObj.index++;//alert(1);
	return oLi;
};
function goinfo(vurl){
	window.location.href=vurl;
}
function rnd(n,m)
{
	return parseInt(Math.random()*(m-n+1)+n);
};
function getJSON()
{
	//return jQuery.parseJSON(""+
		
	//+"");
};
function getCollegeName(index)
{
	collegeName = ["北京大学-Peking University","清华大学-Tsinghua University","上海交通大学-Shanghai Jiao Tong University","复旦大学-Fudan University","北京语言大学-Peking Language University","普林斯顿大学-Princeton University","麻省理工学院-Massachusetts Institute of Technology","悉尼大学-The University of Sydney","西北大学-Northwestern University","耶鲁大学-Yale University","哥伦比亚大学-Columbia University"];
	return collegeName[index];
};
function getCourseName(index)
{
	courseName = ["计算机原理","数字电路","大学英语","大学法语","模拟电路","面向对象程序设计","信息系统架构","中华文化传统","大学物理","大学生就业指导","社会伦理学"];
	return courseName[index];
};
function destroyFall() 
{ 
	var boxs = document.getElementById('fall-body').children; 
	for(var i=0;i<boxs.length;i++)
	{
		boxs[i].innerHTML = '';
	};
};
function refreshFall()
{
	/*
	destroyFall();
	var json = getJSON();
	create4(json);
	//create12(json);
	*/
	destroyFall();
	matchObj.index = 0;
	//var json = getJSON();

	matchObj.aObj = find(0,13);
	//alert(searchObj.district[0]);alert(matchObj.aObj.length);
	var aUl = document.getElementById('fall-body').children;
	for(var i=0;i<aUl.length;i++)
	{
		var oLi = creatLi(matchObj.aObj[matchObj.index]);
		if(oLi!=null) aUl[i].appendChild(oLi);
	};		
	
};
function checkClickedObj(str)
{
	var ul = str;
	var objs = document.getElementById(ul).children;
	var clickedObj = [],clickedNum = 0,aClickedObjIdex = [];
	if(objs[0].className=='live') clickedNum = objs.length;
	else 
	{
		for(var i=1;i<objs.length;i++)
		{
			if(objs[i].className=='live') 
			{
				clickedNum++;
				clickedObj.push(objs[i].getAttribute("name"));//alert(objs[i].getAttribute("name"));
				aClickedObjIdex.push(i);
				//break;
			};
		};	
	};
	if(clickedNum == objs.length-1) 
	{
		objs[0].className = 'live';
		clickedObj=[];
		aClickedObjIdex = [];
	};
	
	//change the object of search
	searchObj[ul] = aClickedObjIdex;//alert(searchObj[ul][0]);
	if(clickedNum == 0) hideSearbar(ul+"searbar");
	else showSearbar(ul+"searbar",clickedObj);
	//if(shouldDelete < 1) deleteBarDiv(ul+"searbar");
	//alert(clickedNum);
};
function showSearbar(str,arr)
{
	var li = str;
	var oLi = document.getElementById(li);
	if(arr.length<1) oLi.getElementsByTagName("span")[0].innerHTML = "全部";
	//if(arr.length<1) oLi.getElementsByTagName("span")[0].innerHTML = "全部";
	else if(arr.length>=1&&arr.length<=3) oLi.getElementsByTagName("span")[0].innerHTML = arr.join(",");//alert(arr.join(","));
	else oLi.getElementsByTagName("span")[0].innerHTML = arr[0]+","+arr[1]+","+arr[2]+"...";
	oLi.style.display = 'block';
};
function hideSearbar(str)
{
	var li = str;var oLi = document.getElementById(li);oLi.style.display = 'none';
};

function create12(json)
{
	//alert(searchObj.district.length);
	var aUl = document.getElementById('fall-body').children;
	a(aUl);var m = 0;
	function a(UL){
		var _UL = UL;
		var newLi = creatLi(json);
		/*
		for(var i=0;i<4;i++)
		{
			if(_UL[i].length<1)
			{
				_UL[i].appendChild(creatLi(json));
			};
		};
		*/
		if(_UL[0])
		{
			var ul = _UL[0];	
			for(var i=1;i<_UL.length;i++)
			{	
				if(ul.offsetHeight>_UL[i].offsetHeight)ul=_UL[i];
			};
		}
		if(newLi) ul.appendChild(newLi);
		m++;if(m < 4){ a(); }; 
	};
			
};