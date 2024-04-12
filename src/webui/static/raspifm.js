function initStationSearch()
{
    $('#tagdisplay1').click(function (e) 
    { 
        // If the clicked element has the class 'delete-button' 
        if (e.target.classList.contains('deletebtn')) { 
            
            // Remove the parent element (the tag) 
            e.target.parentNode.remove();

            let values = $('#tagdisplay1 li').map(function()
            {
                return $(this).contents().get(0).nodeValue;
            }).get().join(','); 

            $('#txtags').val(values);
        } 
    }); 

    $('#tagsearch1').on('keyup', function(e)
    {
        var search = $(this).val().trim();
        if (search != '')
        {
            $.ajax(
            {
                url:'gettags',
                method:'POST',
                data:{filter:search},
                success:function(data)
                {
                    if (!(data === null))
                    {
                        $('#tagres1').html(data);

                        $('#tagres1 li').click(function(e) 
                        { 
                            let tagContent = e.target.innerText.trim(); 
                            if (tagContent !== '')
                            { 
                                let litag = document.createElement('li'); 
                                litag.innerText = tagContent; 
                                // Add delete button
                                litag.innerHTML += '<button class="deletebtn">X</button>'; 
                                $('#tagdisplay1').append(litag); 
                                let values = $('#tagdisplay1 li').map(function()
                                {
                                    return $(this).contents().get(0).nodeValue; 
                                }).get().join(','); 

                                $('#txtags').val(values);
                                $('#tagsearch1').focus();
                            }
                        });
                    }
                    else
                    {
                        $('#tagres1').html('No tag found.');
                    }

                    $('#tagres1').show();
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            });
        }
    });

    $('#tagsearch1').on('focus', function()
    {
        if ($('#tagres1').html())
        {
            if (!$('#tagres1').is(':visible'))
            {
                $('#tagres1').show();
            }
        }
    });


    $(window).on('click', function(e)
    {   
        if (!$('#tagres1')[0].contains(e.target) && e.target.id != 'tagsearch1')
        {
            if ($('#tagres1').is(':visible'))
            {
                $('#tagres1').hide();
            }
        }
    });

    $('#slfavorites').on('change', function(e)
    {   
        $('#txfavlist').val($('#slfavorites').val());

        $.ajax(
            {   
                url:'getfavoritelist',
                method:'POST',
                data:{favlistuuid:$('#slfavorites').val()},
                success:function(data)
                {
                    let stationuuid;
                    $('img[id^="favimg-"]').each(function(index)
                    {
                        stationuuid=$(this).attr('id').substr(7);
                        if (jQuery.inArray(stationuuid, data) > -1)
                        {
                            $(`a[data-stationuuid="${stationuuid}"]`).attr('data-changetype', 'remove');
                            $(this).attr('src', $(this).attr('src').replace('star.svg', 'star-fill.svg'));
                        }
                        else
                        {
                            $(`a[data-stationuuid="${stationuuid}"]`).attr('data-changetype', 'add');
                            $(this).attr('src', $(this).attr('src').replace('star-fill.svg', 'star.svg'));
                        }
                    }); 
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });

    registerFavLinksStationSearch();
}

function initFavListMgmt()
{
    $('#favlistadd').on('click', function(e)
    {
        $.ajax(
            {   url:'addfavoritelist',
                method:'POST',
                success:function(data)
                {         
                    $('#slfavorites').append($('<option>',
                    {
                        value: data,
                        text: '{no name}'
                    }));

                    $('#tblfavoritelists tr:last .favlistmovedown').prop("disabled", false);
                    $('#tblfavoritelists tbody').append(`
                    <tr id="favlistrow-${data}">
                        <td class="align-middle">{no name}</td>
                        <td class="align-middle">
                            <button class="favlistmoveup btn btn-primary btn-sm mb-2" data-changetype="Up" data-favlistuuid="${data}">
                                <img src="/static/arrow-up.svg" width="15em" height="15em" />
                            </button>
                            <button class="favlistmovedown btn btn-primary btn-sm mb-2" data-changetype="Down" data-favlistuuid="${data}" disabled>
                                <img src="/static/arrow-down.svg" width="15em" height="15em" />
                            </button>
                        </td>
                        <td>
                            <div class="btn-group" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="Remove favorite list.">
                                <button class="btn btn-primary btn-sm mb-2 favlistremove" type="button" data-favlistuuid="${data}" data-bs-toggle="modal" data-bs-target="#confirmfavlistremovemodal">
                                    <img src="/static/x.svg" width="15em" height="15em" />
                                </button>
                            </div>
                        </td>
                    </tr>`
                    );
                    
                    $('#tblfavoritelists tbody tr:first .favlistdelete').prop('disabled', false);
                    favlistSelectRow($('#tblfavoritelists tr:last'))
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });

    $('#confirmfavlistdeletemodal').on('show.bs.modal', function(e) {
        let favListUid = $(e.relatedTarget).attr('data-favlistuuid')
        let favlistName = $(`#favlistrow-${favListUid} td:first`).text()
        $('#confirmfavlistdeletemodalContent').attr('data-favlistuuid', favListUid);
        $('#confirmfavlistdeletemodalContent').text(`Really delete favorite list "${favlistName}"?`);
    });

    $('#confirmfavlistdelete').on('click', function(e)
    {
        let confirmfavlistdeletemodal = bootstrap.Modal.getOrCreateInstance(document.getElementById('confirmfavlistdeletemodal'));
        confirmfavlistdeletemodal.hide();

        let favlistuuidToDelete = $('#confirmfavlistdeletemodalContent').attr('data-favlistuuid');

        $.ajax(
            {   url:'deletefavoritelist',
                method:'POST',
                data:{favlistuuid:favlistuuidToDelete},
                success:function(data)
                {
                    let rowToRemove =$(`#favlistrow-${favlistuuidToDelete}`);

                    let wasSelected = false
                    if(rowToRemove.hasClass('favlistselected'))
                    {
                        wasSelected = true
                    }

                    let rowIndex = rowToRemove.index();
                    let maxIndex = $(rowToRemove.parent()[0]).children().length - 1;
                    
                    rowToRemove.remove();
                    if(rowIndex === 0)
                    {
                        $('#tblfavoritelists tbody tr:first .favlistmoveup').prop('disabled', true);
                    }

                    if(rowIndex === maxIndex)
                    {
                        $('#tblfavoritelists tr:last .favlistmovedown').prop('disabled', true);
                    }
                    
                    if(wasSelected)
                    {
                        favlistSelectRow($('#tblfavoritelists tbody tr:first'))
                    }

                    if(maxIndex <= 1)
                    {
                        $('#tblfavoritelists .favlistdelete').prop('disabled', true);
                    }
                },
                error:function(xhr)
                {
                    let errorvar = JSON.parse(xhr.responseText);
                    if (errorvar.errorNo === 1)
                    {
                        $('#errortoastContent').text(errorvar.error[0]); 
                    }
                    else
                    {
                        $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    }

                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });

    $('#tblfavoritelists').on('click', 'tr', function(e)
    {
        favlistSelectRow($(this));
    });   

    $('#tblfavoritelists').on('click', '.favlistmoveup, .favlistmovedown', function(e)
    {
        e.stopPropagation();

        let row = $(this).parent().parent();
        let orgRowIndex = row.index();
        let maxIndex = $(row.parent()[0]).children().length - 1;
        let favlistUuidToMove = $(this).attr('data-favlistuuid');
        let direction = $(this).attr('data-changetype');

        $.ajax(
            {   
                url:'movefavoritelist',
                method:'POST',
                data:{favlistuuid:favlistUuidToMove, direction:direction},
                success:function(data)
                {
                    if (direction==='Up') {
                        row.insertBefore(row.prev());

                        if(orgRowIndex===maxIndex)
                        {
                            let button = row.find('.favlistmovedown');
                            button.prop('disabled', false);
                            button = row.next().find('.favlistmovedown');
                            button.prop('disabled', true);
                        }

                        if(row.index()===0)
                        {
                            let button = row.find('.favlistmoveup');
                            button.prop('disabled', true);
                            button = row.next().find('.favlistmoveup');
                            button.prop('disabled', false);
                        }
                    }
                    
                    if (direction==='Down')
                    {
                        row.insertAfter(row.next());

                        if(orgRowIndex===0)
                        {
                            let button = row.find('.favlistmoveup');
                            button.prop('disabled', false);
                            button = row.prev().find('.favlistmoveup');
                            button.prop('disabled', true);
                        }

                        if(row.index()===maxIndex)
                        {
                            let button = row.find('.favlistmovedown');
                            button.prop('disabled', true);
                            button = row.prev().find('.favlistmovedown');
                            button.prop('disabled', false);
                        }
                    }
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });

    $('#stationstable').on('click', '.stationmoveup, .stationmovedown', function(e)
    {
        let row = $(this).parent().parent();
        let orgRowIndex = row.index();
        let maxIndex = $(row.parent()[0]).children().length - 1;
        let favlistUuidToMove = $('#tblfavoritelists .favlistselected').attr('id').substr(11)
        let stationUuidToMove = $(this).attr('data-stationuuid');
        let direction = $(this).attr('data-changetype');

        $.ajax(
            {   
                url:'movestationinfavoritelist',
                method:'POST',
                data:{favlistuuid:favlistUuidToMove, stationuuid:stationUuidToMove, direction:direction},
                success:function(data)
                {
                    if (direction==='Up') {
                        row.insertBefore(row.prev());

                        if(orgRowIndex===maxIndex)
                        {
                            let button = row.find('.stationmovedown');
                            button.prop('disabled', false);
                            button = row.next().find('.stationmovedown');
                            button.prop('disabled', true);
                        }

                        if(row.index()===0)
                        {
                            let button = row.find('.stationmoveup');
                            button.prop('disabled', true);
                            button = row.next().find('.stationmoveup');
                            button.prop('disabled', false);
                        }
                    }
                    
                    if (direction==='Down')
                    {
                        row.insertAfter(row.next());

                        if(orgRowIndex===0)
                        {
                            let button = row.find('.stationmoveup');
                            button.prop('disabled', false);
                            button = row.prev().find('.stationmoveup');
                            button.prop('disabled', true);
                        }

                        if(row.index()===maxIndex)
                        {
                            let button = row.find('.stationmovedown');
                            button.prop('disabled', true);
                            button = row.prev().find('.stationmovedown');
                            button.prop('disabled', false);
                        }
                    }
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });

    $('#tblfavoritelists').on('click', '.favlistdelete', function(e)
    {
        e.stopPropagation();
    });

    registerFavLinksFavManagement();
}

function registerFavListEditControls()
{
    $('#txname').on('keyup', function(e)
    {
        delay(function()
        {
            let newvalue = $('#txname').val();
            let favlistuuid = $('#tblfavoritelists .favlistselected').attr('id').substr(11);

            $.ajax(
                {   url:'changefavoritelist',
                    method:'POST',
                    data:{favlistuuid:favlistuuid, property:'name', value:newvalue},
                    success:function(data)
                    {
                        $('#slfavorites option:selected').text(newvalue);
                        $(`#tblfavoritelists #favlistrow-${favlistuuid} td:first`).text(newvalue);
                    },
                    error:function(xhr)
                    {
                        $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                        let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                        errortoast.show();
                    }
                }
            );

        }, 500 );
    });

    $('#chdefault').on('change', function(e)
    {
        $.ajax(
            {   url:'changefavoritelist',
                method:'POST',
                data:{favlistuuid:$('#tblfavoritelists .favlistselected').attr('id').substr(11),property:'isdefault', value:$('#chdefault').prop('checked')},
                success:function(data)
                {

                },
                error:function(xhr)
                {
                    $('#chdefault').prop('checked', 'checked');
                    let errorvar = JSON.parse(xhr.responseText);
                    if (errorvar.errorNo === 1)
                    {
                        $('#errortoastContent').text(errorvar.error[0]); 
                    }
                    else
                    {
                        $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    }

                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });
}

function registerFavLinksStationSearch()
{
    $('.fav-link').on('click', function(e)
    {
        let changetype = $(this).attr('data-changetype');
        let stationuuid = $(this).attr('data-stationuuid');

        $.ajax(
            {   url:'changefavorite',
                method:'POST',
                data:{changetype:changetype, stationuuid:stationuuid, favlistuuid:$('#slfavorites').val()},
                context:$(this),
                success:function(data)
                {   
                    let img = $('img', this);
                    if (changetype==='add')
                    {
                        $(this).attr('data-changetype', 'remove');
                        img.attr('src', img.attr('src').replace('star.svg', 'star-fill.svg'));
                    }
                    else
                    {
                        $(this).attr('data-changetype', 'add');
                        img.attr('src', img.attr('src').replace('star-fill.svg', 'star.svg'));
                    }
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });
}

function registerFavLinksFavManagement()
{
    $('.fav-link').on('click', function(e)
    {
        let changetype = $(this).attr('data-changetype');
        let stationuuid = $(this).attr('data-stationuuid');
        let tester = $('#tblfavoritelists .favlistselected').attr('id').substr(11);
        $.ajax(
            {   url:'changefavorite',
                method:'POST',
                data:{changetype:changetype, stationuuid:stationuuid, favlistuuid:$('#tblfavoritelists .favlistselected').attr('id').substr(11)},
                context:$(this),
                success:function(data)
                {   
                    let row = $(`#favrow-${stationuuid}`);
                    row.fadeOut(1000, function() {
                        row.remove();
                    });
                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });
}

function favlistSelectRow(row)
{
    $('#tblfavoritelists .favlistselected').removeClass('table-bg-raspicolor favlistselected');
    row.addClass('favlistselected table-bg-raspicolor');

    let favlistUuid = row.attr('id').substr(11);

    $.ajax(
        {   url:'getfavoritelistcontent',
            method:'POST',
            data:{favlistuuid:favlistUuid},
            success:function(data)
            {
                $('#favcontent').html(data);
                registerFavLinksFavManagement();
                registerFavListEditControls();
            },
            error:function(xhr)
            {
                $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                errortoast.show();
            }
        }
    );
}

function initSettingsMgmt()
{
    $('#slcountry').on('change', function(e)
    {   
        $.ajax(
            {   
                url:'changesettings',
                method:'POST',
                data:{property:'country', value:$('#slcountry').val()},
                success:function(data)
                {

                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });$('#tblfavoritelists .favlistselected').attr('id').substr(11)

    $('#sllang').on('change', function(e)
    {   
        $.ajax(
            {
                url:'changesettings',
                method:'POST',
                data:{property:'lang', value:$('#sllang').val()},
                success:function(data)
                {

                },
                error:function(xhr)
                {
                    $('#errortoastContent').text(`Something went wrong, the server responded: ${xhr.responseText}.`);
                    let errortoast = bootstrap.Toast.getOrCreateInstance(document.getElementById('errortoast'));
                    errortoast.show();
                }
            }
        );
    });
}

function initToolTips()
{
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    const toastElList = document.querySelectorAll('.toast');
    const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl));
}

let delay = (()=>{
    let timer = 0;
    return function(callback, ms){
      clearTimeout (timer);
      timer = setTimeout(callback, ms);
    };
  })();