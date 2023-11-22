function initStationSearch()
{
    $("#tagdisplay1").click(function (e) 
    { 
        // If the clicked element has the class 'delete-button' 
        if (e.target.classList.contains('deletebtn')) { 
            
            // Remove the parent element (the tag) 
            e.target.parentNode.remove();

            let values = $('#tagdisplay1 li').map(function()
            {
                return $(this).contents().get(0).nodeValue; 
            }).get().join(','); 

            $("#txtags").val(values)
        } 
    }); 

    $('#tagsearch1').on("keyup", function(e)
    {
        var search = $(this).val().trim();
        if(search != "")
        {
            $.ajax(
            {
                url:"gettags",
                method:"POST",
                data:{filter:search},
                success:function(data)
                {
                    if (data)
                    {
                        $("#tagres1").html(data);

                        $("#tagres1 li").click(function(e) 
                        { 
                            let tagContent = e.target.innerText.trim(); 
                            if (tagContent !== "")
                            { 
                                let litag = document.createElement("li"); 
                                litag.innerText = tagContent; 
                                // Add delete button
                                litag.innerHTML += "<button class=\"deletebtn\">X</button>"; 
                                $("#tagdisplay1").append(litag); 
                                let values = $('#tagdisplay1 li').map(function()
                                {
                                    return $(this).contents().get(0).nodeValue; 
                                }).get().join(','); 

                                $("#txtags").val(values);
                                $("#tagsearch1").focus();
                            }
                        });
                    }
                    else
                    {
                        $("#tagres1").html("No tag found.");
                    }

                    $("#tagres1").show();
                },
                error:function(xhr, textStatus, errorThrown)
                {
                    $("#errortoastContent").text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById("errortoast"));
                    errortoast.show()
                }
            });
        }
    });

    $("#tagsearch1").on("focus", function()
    {
        if($("#tagres1").html())
        {
            if(!$("#tagres1").is(":visible"))
            {
                $("#tagres1").show();
            }
        }
    });


    $(window).on("click", function(e)
    {   
        if (!$("#tagres1")[0].contains(e.target) && e.target.id != "tagsearch1")
        {
            if($("#tagres1").is(":visible"))
            {
                $("#tagres1").hide();
            }
        }
    });

    $("#slfavorites").on("change", function(e)
    {   
        $("#txfavlist").val($("#slfavorites").val())
        $.ajax(
            {   url:"getfavoritelist",
                method:"POST",
                data:{favlistuuid:$("#slfavorites").val()},
                success:function(data)
                {
                    let imgid
                    $('img[id^="favimg-"]').each(function( index)
                    {
                        imgid=$(this).attr("id").substr(7)
                        if(jQuery.inArray(imgid, data) > -1)
                        {
                            $(this).attr("src", $(this).attr("src").replace("star.svg", "star-fill.svg"));
                        }
                        else
                        {
                            $(this).attr("src", $(this).attr("src").replace("star-fill.svg", "star.svg"));
                        }
                    }); 
                },
                error:function(xhr, textStatus, errorThrown)
                {
                    $("#errortoastContent").text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById("errortoast"));
                    errortoast.show()
                }
            }
        );
    });

    registerFavLinks();
}

function initFavListMgmt()
{
    $('#favlistadd').on("click", function(e)
    {
        $.ajax(
            {   url:"addfavoritelist",
                method:"POST",
                success:function(data)
                {         
                    $('#slfavorites').append($('<option>',
                    {
                        value: data,
                        text: "{no name}"
                    }));

                    $(`#slfavorites option[value=${data}]`).attr('selected', 'selected');
                    $('#slfavorites').trigger("change");
                },
                error:function(xhr, textStatus, errorThrown)
                {
                    $("#errortoastContent").text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById("errortoast"));
                    errortoast.show()
                }
            }
        );
    });

    $("#slfavorites").on("change", function(e)
    {   
        let favoritelistname = $("#slfavorites option:selected").text()
        $.ajax(
            {   url:"getfavoritelistcontent",
                method:"POST",
                data:{favlistuuid:$("#slfavorites").val()},
                success:function(data)
                {
                    $("#favcontent").html(data);
                    registerFavConfirmRemove();
                    registerFavLinks();
                    $("#confirmfavlistremovemodalContent").text(`Really delete favorite list "${favoritelistname}"?`);
                },
                error:function(xhr, textStatus, errorThrown)
                {
                    $("#errortoastContent").text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById("errortoast"));
                    errortoast.show()
                }
            }
        );
    });

    registerFavConfirmRemove();
    registerFavLinks(true);
}

function registerFavConfirmRemove()
{
    $('#confirmfavlistremove').on("click", function(e)
    {
        let confirmfavlistremovemodal = bootstrap.Modal.getOrCreateInstance(document.getElementById("confirmfavlistremovemodal"));
        confirmfavlistremovemodal.hide();
        let favlistuuidToDelete = $("#slfavorites").val()
        $.ajax(
            {   url:"removefavoritelist",
                method:"POST",
                data:{favlistuuid:favlistuuidToDelete},
                success:function(data)
                {
                    $(`#slfavorites option[value="${favlistuuidToDelete}"]`).remove();
                    $('#slfavorites').trigger("change");
                },
                error:function(xhr, textStatus, errorThrown)
                {
                    let errorvar = JSON.parse(xhr.responseText);
                    if(errorvar.errorNo == 1)
                    {
                        $("#errortoastContent").text(`Last favorite list cannot be deleted.`); 
                    }
                    else
                    {
                        $("#errortoastContent").text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    }

                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById("errortoast"));
                    errortoast.show()
                }
            }
        );
    });
}

function registerFavLinks(removetablerow = false)
{
    $('.fav-link').on("click", function(e)
    {
        let changetype = $(this).attr("data-changetype")
        let stationuuid = $(this).attr("data-stationuuid")

        $.ajax(
            {   url:"changefavorite",
                method:"POST",
                data:{changetype:changetype, stationuuid:stationuuid, favlistuuid:$("#slfavorites").val()},
                context:$(this),
                success:function(data)
                {   
                    if(removetablerow)
                    {
                        let row = $(`#favrow-${stationuuid}`);
                        row.fadeOut(1000, function() {
                            row.remove();
                        });
                    }   
                    else
                    {
                        let img = $("img", this)  
                        if(changetype=="add")
                        {
                            $(this).attr("data-changetype", "remove");
                            img.attr("src", img.attr("src").replace("star.svg", "star-fill.svg"));
                        }
                        else
                        {
                            $(this).attr("data-changetype", "add");
                            img.attr("src", img.attr("src").replace("star-fill.svg", "star.svg"));
                        }
                    }
                },
                error:function(xhr)
                {
                    $("#errortoastContent").text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById("errortoast"));
                    errortoast.show()
                }
            }
        );
    });
}

function initToolTips()
{
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

    const toastElList = document.querySelectorAll(".toast")
    const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl))
}

