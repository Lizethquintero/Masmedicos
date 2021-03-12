$('.product_image .img').css('max-width','220px');
$('.product_image .img').css('max-height','123');
$('#submit_beneficiaries').css('margin-top','-220px');

odoo.define('web_sale_extended.show_website_cities', function(require) {
    'use strict';

    $(function() {
        $('#country_id').selectpicker();
        $('#state_id').selectpicker('val', '');
        $('#fiscal_position_id').selectpicker();
        $('#city').selectpicker();
        $('#document').selectpicker('val', '');
        $('#fiscal_position').selectpicker();

        function consultarZipcode(ciudad){
            $.ajax({
                data: { 'city_id': ciudad },
                url: "/search/zipcodes",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    document.querySelector("input[name='zip']").value = decode_data['data'].zipcode;
                    document.querySelector("input[name='zip_id']").value = decode_data['data'].zipid;
                }
            });
        }

        $('#city').change(function() {
            let data_select = $("#city option:selected").val();
            consultarZipcode(data_select);
        });

        function consultarCiudades(estado, elemento) {
            $.ajax({
                data: { 'departamento': estado },
                url: "/search/cities",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    let elemento_completo = $(elemento);
                    $('#city').selectpicker('destroy');
                    $('#city').empty();
                    decode_data.data.cities.forEach(function(obj) {
                        $('#city').append($("<option></option>")
                            .attr("value", obj.city_id).text(obj.city));
                    });
                    $('#city').selectpicker();
                    let data_select = $("#city option:selected").val();
                    consultarZipcode(data_select);
                }
            });
        }

        $("select[name='state_id']").on('change', function cambiarEstado() {
            let estado = $(this).val();
            let elemento = "select[name='city']";
            if (estado != ''){
                consultarCiudades(estado, elemento);
            } else {
                $('#city').selectpicker('destroy');
                $('#city').empty();
                $('#city').append($("<option></option>")
                            .attr("value", '').text('Ciudad...'));
                $('#city').selectpicker();
            }
        });

        $("input[name='bfdate1']").on('change', function calcularEdad() {
            let fecha = $(this).val();
            let hoy = new Date();
            let cumpleanos = new Date(fecha);
            let edad = hoy.getFullYear() - cumpleanos.getFullYear();
            let m = hoy.getMonth() - cumpleanos.getMonth();
            if (m < 0 || (m === 0 && hoy.getDate() < cumpleanos.getDate())) {
                edad--;
            }
            let email_asegurador = $("input[name='email']").val();
            let telefono_fijo_asegurador = $("input[name='fijo']").val();
            let ciudad_asegurador = $("input[name='city']").val();
            let adress_asegurador = $("input[name='address']").val();
            let asegurador_state = $("input[name='deparment']").val();
            let country_asegurador = $("input[name='country_id']").val();
            let fiscal_position_asegurador = $("input[name='fiscal_position_id']").val();
            if (edad < 18) {
                console.log("Eres menor de edad");

                $("input[name='bfemail1']").val(email_asegurador);
                $("input[name='bfaddress1']").val(adress_asegurador);
                //$("select[name='bfcountry_id1']").val(country_asegurador);
                //$("select[name='bfdeparment1']").val(asegurador_state);
                //$("select[name='bfcity1']").val(ciudad_asegurador);
                $("input[name='bffijo1']").val(telefono_fijo_asegurador);

            }
        });


        $.validator.addMethod("formMovilFijoLength", function (value, element) {
           if(element.value.length == 7 || element.value.length == 10){
              return true;
           } else {
              return false;
           }
        }, "¡Upss! debe tener 7 ó 10 digitos");


        $.validator.addMethod("lettersonly", function(value, element) {
            return this.optional(element) || /^[a-zA-ZÀ-ÿ\u00f1\u00d1]+(\s*[a-zA-ZÀ-ÿ\u00f1\u00d1]*)*[a-zA-ZÀ-ÿ\u00f1\u00d1]/g.test(value);
        }, "¡Upss! deben ser ser solo letras");


        $("#terminos").hide();
        $("#politica").hide();
        $("#shop").validate({
            rules: {
                name: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                lastname: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                othernames: {
                    lettersonly: true,
                },
                lastname2: {
                    lettersonly: true,
                },
                email: {
                    required: true,
                    email: true
                },
                phone: {
                    required: true,
                    number: true,
                    formMovilFijoLength: true,
                },
                document: {
                    required: true
                },
                identification_document: {
                    required: true,
                    number: true,
                },
                street: {
                    required: true,
                },
                city: {
                    required: true,
                },
                country_id: {
                    required: true,
                },
                state_id: {
                    required: true,
                },
                aceptacion_datos: {
                    required: true
                },
                tyc: {
                    required: true
                },
                birthdate_date: {
                    required: true,
                    max: {
                        depends: function(elem) {
                            var edad_maxima = 0;
                            let fecha = $("input[name='birthdate_date']").val();

                            let hoy = new Date();
                            let cumpleanos = new Date(fecha);
                            let edad = hoy.getFullYear() - cumpleanos.getFullYear();
                            let m = hoy.getMonth() - cumpleanos.getMonth();
                            if (m < 0 || (m === 0 && hoy.getDate() < cumpleanos.getDate())) {
                                edad--;
                            }
                            return edad > 69
                        }
                    },
                    min: {
                        depends: function(elem) {
                            var edad_maxima = 0;
                            let fecha = $("input[name='birthdate_date']").val();
                            let hoy = new Date();
                            let cumpleanos = new Date(fecha);
                            let edad = hoy.getFullYear() - cumpleanos.getFullYear();
                            let m = hoy.getMonth() - cumpleanos.getMonth();
                            if (m < 0 || (m === 0 && hoy.getDate() < cumpleanos.getDate())) {
                                edad--;
                            }

                            return edad < 18
                        }
                    }
                },
                expedition_date: {
                    required: true,

                }
            },
            messages: {
                name: {
                    required: "¡Upss! tu nombre es requerido",
                    minlength: "Un nombre contiene más de 3 caracteres"
                },
                lastname: {
                    required: "¡Upss! tu apellido es requerido",
                    minlength: "¡Upss! tu apellido debe contener más de 3 caracteres"
                },
                // lastname2: {
                //     required: "Este campo es requerido",
                //     minlength: "Un apellido contiene más de 3 caracteres"
                // },
                email: {
                    required: "¡Upss! tu email es requerido",
                    email: "¡Upss! escribe un email valido"
                },
                phone: {
                    required: "¡Upss! tu telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos"

                },
                document: {
                    required: "¡Upss! tu tipo de documento es requerido",

                },
                identification_document: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "¡Upss! este campo solo es numérico"

                },
                street: {
                    required: "¡Upss! tu dirección es requerida",

                },
                city: {
                    required: "¡Upss! tu ciudad es requerida",

                },
                country_id: {
                    required: "¡Upss! tu país es requerido",
                },
                state_id: {
                    required: "¡Upss! tu departamento es requerido",

                },
                aceptacion_datos: {
                    required: "¡Upss! Acepte política de tratamiento de datos para continuar",

                },
                tyc: {
                    required: "¡Upss! Acepte terminos y condiciones para continuar",

                },
                birthdate_date: {
                    required: "¡Upss! tu fecha de nacimiento es requerido",
                    min: "¡Upss! Tienes que ser mayor de edad",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"

                },
                expedition_date: {
                    required: "¡Upss! tu fecha de expedición es requerido",
                },

            }
        });
        hide_beneficiaries();
    });


    function hide_beneficiaries() {
        $("#beneficiary1").hide();
        $("#beneficiary2").hide();
        $("#beneficiary3").hide();
        $("#beneficiary4").hide();
        $("#beneficiary5").hide();
        $("#beneficiary6").hide();

    }


    $("#cant_beneficiarios").on('change', function mostrarbeneficiarios() {
        let cantidad_beneficiarios = parseInt($(this).val());
        if (cantidad_beneficiarios == 0 || cantidad_beneficiarios == '0') {
            hide_beneficiaries();
        } else {
            hide_beneficiaries();
            for (let index = 0; index < cantidad_beneficiarios; index++) {

                let id_elemento = "#beneficiary" + (index + 1);
                let id_subti = "#subti" + (index + 1);
                let subtitulo = "Datos del beneficiario " + (index + 1) + " de " + cantidad_beneficiarios;

                $(id_subti).text(subtitulo);
                $(id_elemento).show();

                //var beneficiaries_number = $("input[name='beneficiaries_number']").val();
                //var beneficiaries_number = $("input[name='beneficiario']").val();

                //alert(cantidad_beneficiarios);

                if (cantidad_beneficiarios == 1){
                    $('#submit_beneficiaries').css('margin-top','-160px');
                } else if (cantidad_beneficiarios == 2){
                    $('#submit_beneficiaries').css('margin-top','-130px');
                } else if (cantidad_beneficiarios == 3){
                    $('#submit_beneficiaries').css('margin-top','-90px');
                } else if (cantidad_beneficiarios == 4){
                    $('#submit_beneficiaries').css('margin-top','-50px');
                } else if (cantidad_beneficiarios == 5){
                    $('#submit_beneficiaries').css('margin-top','-20px');
                } else if (cantidad_beneficiarios == 6){
                    $('#submit_beneficiaries').css('margin-top','20px');
                }

            }
        }
    });
    $("select[name='estado_civil']").on('change', function cambiarConyugues() {
        console.log("cambio");

        let estado = $(this).val();
        if (estado == 'Soltero') {
            let newOptions = {
                Seleccione: "",
                Padres: "D",
                Hijos: "H",
                Hermanos: "M"
            };
            for (let index = 0; index < 6; index++) {
                let id_elemento = 'bfparentesco' + (index + 1);
                console.log(id_elemento);
                let elemento = "select[name='" + id_elemento + "']";
                console.log(elemento);
                let elemento_completo = $(elemento);
                console.log(elemento_completo);
                elemento_completo.empty();
                $.each(newOptions, function(key, value) {
                    elemento_completo.append($("<option></option>")
                        .attr("value", value).text(key));
                });

            }

        } else if (estado == 'Viudo') {
            let newOptions = {
                Seleccione: "",
                Padres: "D",
                Hijos: "H",
                Hermanos: "M",
                Suegros: "S"
            };
            for (let index = 0; index < 6; index++) {
                let id_elemento = 'bfparentesco' + (index + 1);
                console.log(id_elemento);
                let elemento = "select[name='" + id_elemento + "']";
                console.log(elemento);
                let elemento_completo = $(elemento);
                console.log(elemento_completo);
                elemento_completo.empty();
                $.each(newOptions, function(key, value) {
                    elemento_completo.append($("<option></option>")
                        .attr("value", value).text(key));
                });

            }

        } else {
            let newOptions = {
                Seleccione: "",
                Cónyuge: "C",
                Padres: "D",
                Hijos: "H",
                Hermanos: "M",
                Suegros: "S"
            };
            for (let index = 0; index < 6; index++) {
                let id_elemento = 'bfparentesco' + (index + 1);
                console.log(id_elemento);
                let elemento = "select[name='" + id_elemento + "']";
                console.log(elemento);
                let elemento_completo = $(elemento);
                console.log(elemento_completo);
                elemento_completo.empty();
                $.each(newOptions, function(key, value) {
                    elemento_completo.append($("<option></option>")
                        .attr("value", value).text(key));
                });

            }

        }

    });



       /*
        $('#country_id').change(function() {
            let data_select = $("#country_id option:selected").val();
            if (data_select != '49'){

                $.ajax({
                    data: { 'country': data_select },
                    url: "/search/cities",
                    type: 'get',
                    success: function(data) {
                        alert('llegando')
                    }
                });
            }
        });*/


    function consultarCiudadesBeneficiary(estado, elemento, item) {
            $.ajax({
                data: { 'departamento': estado },
                url: "/search/cities",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    let elemento_completo = $(elemento);
                    if (item == 0) {
                        $('#bfcity0').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity0').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    } else if (item == 1) {
                        $('#bfcity1').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity1').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    } else if (item == 2) {
                        $('#bfcity2').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity2').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    } else if (item == 3) {
                        $('#bfcity3').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity3').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    } else if (item == 4) {
                        $('#bfcity4').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity4').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    }  else if (item == 5) {
                        $('#bfcity5').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity5').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    }
                }
            });
        }


    $("select[id='bfdeparment0']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[id='bfcity0']";
        consultarCiudadesBeneficiary(estado, elemento, 0);

    });
    $("select[name='bfdeparment1']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[name='bfcity1']";
        consultarCiudadesBeneficiary(estado, elemento, 1);

    });
    $("select[name='bfdeparment2']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[name='bfcity2']";
        consultarCiudadesBeneficiary(estado, elemento, 2);

    });
    $("select[name='bfdeparment3']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[name='bfcity3']";
        consultarCiudadesBeneficiary(estado, elemento, 3);

    });
    $("select[name='bfdeparment4']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[name='bfcity4']";
        consultarCiudadesBeneficiary(estado, elemento, 4);

    });
    $("select[name='bfdeparment5']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[name='bfcity5']";
        consultarCiudadesBeneficiary(estado, elemento, 5);

    });

    $("#btn_terminos").click(function() {
        $("#politica").hide();
        $("#terminos").show();

    });
    $("#btn_politica").click(function() {
        $("#terminos").hide();
        $("#politica").show();

    });


    $("#posicion_fiscal_help_icon").on('click', function posicion_fiscal_help() {
        $("#posicion_fiscal_help").toggle();
    });

    $("#posicion_fiscal_help_icon").on('mouseover', function posicion_fiscal_help() {
        $("#posicion_fiscal_help").show();
    });





    // $('#exampleModal').modal();
    // $('#exampleModal').on('shown.bs.modal', function() {
    // $('#myInput').trigger('focus')
    // });




    /* document.getElementById('cant_beneficiarios').addEventListener('change', function() {
         let cantidad_beneficiarios = parseInt(this.value);
         if (cantidad_beneficiarios == 0) {
             hide_beneficiaries();
         } else {
             for (let index = 0; index < cantidad_beneficiarios; index++) {
                 let id_elemento = "#beneficiary" + (index + 1);
                 let id_subti = "#subti" + (index + 1);
                 let subtitulo = "Datos del beneficiario " + (index + 1) + " de " + cantidad_beneficiarios;
                 console.log(subtitulo);
                 $(id_subti).text(subtitulo);
                 $(id_elemento).show();


             }
         }

     });*/
    // var ajax = require('web.ajax');
    // var core = require('web.core');
    // var sAnimation = require('website.content.snippets.animation');

    // var qweb = core.qweb;
    // var _t = core._t;
    // var ajax = require('web.ajax');
    // var dest = 0;

    // sAnimation.registry.OdooWebsiteSearchCity = sAnimation.Class.extend({
    //     selector: ".search-query-city",
    //     autocompleteMinWidth: 300,
    //     init: function() {
    //         console.log('init: search_city');
    //     },
    //     start: function() {
    //         var self = this;

    //         this.$target.attr("autocomplete", "off");
    //         this.$target.parent().addClass("typeahead__container");
    //         this.$target.typeahead({
    //             minLength: 1,
    //             maxItem: 15,
    //             delay: 500,
    //             order: "asc",
    //             cache: false,
    //             hint: true,
    //             accent: true,
    //             //           autofocus: true,
    //             //mustSelectItem: true,
    //             //item: 5334,
    //             //display: ["id","city"],
    //             display: ["city"],
    //             template: '<span>' +
    //                 '<span>{{city}}</span>' +
    //                 '</span>',
    //             source: { city: { url: [{ type: "GET", url: "/search/suggestion_city", data: { query: "{{query}}" }, }, "data.cities"] }, },
    //             callback: {
    //                 onClickAfter: function(node, a, item, event) {
    //                     console.log("CLICK");
    //                 }
    //             }
    //         });
    //     },
    //     debug: true,
    // });





});



odoo.define('web_sale_extended.subscription_add_beneficiaries', function(require) {
    'use strict';

    $(".portal_subscription_beneficiaries_change").on('click', function(e){

      var url_path = '/my/subscription/beneficiaries/';
      var subscription_id = $("input[name='subscription_id']").val();
      var url = url_path + subscription_id;
      window.location.href = url;
    });

    $.validator.addMethod("formMovilFijoLength", function (value, element) {
        if(element.value.length == 7 || element.value.length == 10){
            return true;
        } else {
            return false;
        }
    }, "¡Upss! debe tener 7 ó 10 digitos");

    $.validator.addMethod("lettersonly", function(value, element) {
        return this.optional(element) || /^[a-zA-ZÀ-ÿ\u00f1\u00d1]+(\s*[a-zA-ZÀ-ÿ\u00f1\u00d1]*)*[a-zA-ZÀ-ÿ\u00f1\u00d1]+$/g.test(value);
    }, "¡Upss! deben ser ser solo letras");



    $("#beneficiary").validate({
            rules: {
                name: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                lastname: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                othername: {
                    lettersonly: true,
                },
                lastname2: {
                    lettersonly: true,
                },
                email: {
                    required: true,
                    email: true
                },
                phone: {
                    required: true,
                    number: true,
                    formMovilFijoLength: true,
                },
                fijo: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                document_type: {
                    required: true
                },
                estado_civil: {
                    required: true
                },
                numero_documento: {
                    required: true,
                    number: true,
                },
                address: {
                    required: true,
                },
                city: {
                    required: true,
                },
                country_id: {
                    required: true,
                },
                state_id: {
                    required: true,
                },
                date: {
                    required: true,
                    max: {
                        depends: function(elem) {
                            var edad_maxima = 0;
                            let fecha = $("input[name='date']").val();
                            let hoy = new Date();
                            let cumpleanos = new Date(fecha);
                            let edad = hoy.getFullYear() - cumpleanos.getFullYear();
                            let m = hoy.getMonth() - cumpleanos.getMonth();
                            if (m < 0 || (m === 0 && hoy.getDate() < cumpleanos.getDate())) {
                                edad--;
                            }
                            return edad > 69
                        }
                    },
                    min: {
                        depends: function(elem) {
                            var edad_maxima = 0;
                            let fecha = $("input[name='date']").val();
                            let hoy = new Date();
                            let cumpleanos = new Date(fecha);
                            let edad = hoy.getFullYear() - cumpleanos.getFullYear();
                            let m = hoy.getMonth() - cumpleanos.getMonth();
                            if (m < 0 || (m === 0 && hoy.getDate() < cumpleanos.getDate())) {
                                edad--;
                            }
                            return edad < 18
                        }
                    }
                },
                // beneficiario1 ///////////////////////////
                bfirstname1: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname1: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bfothername1: {
                    lettersonly: true,
                },
                bflastname12: {
                    lettersonly: true,
                },
                bfemail1: {
                    required: true,
                    email: true
                },
                bfphone1: {
                    required: true,
                    number: true,
                    minlength:10,
                    maxlength:10,
                },
                bffijo1: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                bfparentesco1: {
                    required: true,
                },
                bfdocument1: {
                    required: true
                },
                bfnumero_documento1: {
                    required: true,
                    number: true,
                },
                bfaddress1: {
                    required: true,
                },
                bfcity1: {
                    required: true,
                },
                bfcountry_id1: {
                    required: true,
                },
                bfdeparment1: {
                    required: true,
                },
                bfdate1: {
                    required: true,
                },
                // beneficiario2 //////////////////////////////////////////
                bfirstname2: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname2: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bfothername2: {
                    lettersonly: true,
                },
                bflastname22: {
                    lettersonly: true,
                },
                bfemail2: {
                    required: true,
                    email: true
                },
                bfphone2: {
                    required: true,
                    number: true,
                    minlength:10,
                    maxlength:10,
                },
                bffijo2: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                bfparentesco2: {
                    required: true,
                },
                bfdocument2: {
                    required: true
                },
                bfnumero_documento2: {
                    required: true,
                    number: true,
                },
                bfaddress2: {
                    required: true,
                },
                bfcity2: {
                    required: true,
                },
                bfcountry_id2: {
                    required: true,
                },
                bfdeparment2: {
                    required: true,
                },
                bfdate2: {
                    required: true,
                },
                // beneficiario3 //////////////////////////////////////////
                bfirstname3: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname3: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bfothername3: {
                    lettersonly: true,
                },
                bflastname33: {
                    lettersonly: true,
                },
                bfemail3: {
                    required: true,
                    email: true
                },
                bfphone3: {
                    required: true,
                    number: true,
                    minlength:10,
                    maxlength:10,
                },
                bffijo3: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                bfparentesco3: {
                    required: true,
                },
                bfdocument3: {
                    required: true
                },
                bfnumero_documento3: {
                    required: true,
                    number: true,
                },
                bfaddress3: {
                    required: true,
                },
                bfcity3: {
                    required: true,
                },
                bfcountry_id3: {
                    required: true,
                },
                bfdeparment3: {
                    required: true,
                },
                bfdate3: {
                    required: true,
                },
                // beneficiario4 //////////////////////////////////////////
                bfirstname4: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname4: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bfothername4: {
                    lettersonly: true,
                },
                bflastname44: {
                    lettersonly: true,
                },
                bfemail4: {
                    required: true,
                    email: true
                },
                bfphone4: {
                    required: true,
                    number: true,
                    minlength:10,
                    maxlength:10,
                },
                bffijo4: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                bfparentesco4: {
                    required: true,
                },
                bfdocument4: {
                    required: true
                },
                bfnumero_documento4: {
                    required: true,
                    number: true,
                },
                bfaddress4: {
                    required: true,
                },
                bfcity4: {
                    required: true,
                },
                bfcountry_id4: {
                    required: true,
                },
                bfdeparment4: {
                    required: true,
                },
                bfdate4: {
                    required: true,
                },
                // beneficiario5 //////////////////////////////////////////
                bfirstname5: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname5: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bfothername5: {
                    lettersonly: true,
                },
                bflastname55: {
                    lettersonly: true,
                },
                bfemail5: {
                    required: true,
                    email: true
                },
                bfphone5: {
                    required: true,
                    number: true,
                    minlength:10,
                    maxlength:10,
                },
                bffijo5: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                bfparentesco5: {
                    required: true,
                },
                bfdocument5: {
                    required: true
                },
                bfnumero_documento5: {
                    required: true,
                    number: true,
                },
                bfaddress5: {
                    required: true,
                },
                bfcity5: {
                    required: true,
                },
                bfcountry_id5: {
                    required: true,
                },
                bfdeparment5: {
                    required: true,
                },
                bfdate5: {
                    required: true,
                },
                // beneficiario6 //////////////////////////////////////////
                bfirstname6: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname6: {
                    required: true,
                    minlength: 3,
                    lettersonly: true,
                },
                bfothername6: {
                    lettersonly: true,
                },
                bflastname66: {
                    lettersonly: true,
                },
                bfemail6: {
                    required: true,
                    email: true
                },
                bfphone6: {
                    required: true,
                    number: true,
                    minlength:10,
                    maxlength:10,
                },
                bffijo6: {
                    required: false,
                    number: true,
                    minlength:7,
                    maxlength:7,
                },
                bfparentesco6: {
                    required: true,
                },
                bfdocument6: {
                    required: true
                },
                bfnumero_documento6: {
                    required: true,
                    number: true,
                },
                bfaddress6: {
                    required: true,
                },
                bfcity6: {
                    required: true,
                },
                bfcountry_id6: {
                    required: true,
                },
                bfdeparment6: {
                    required: true,
                },
                bfdate6: {
                    required: true,
                },
                ////////////////////////////////////////////
            },
            messages: {
                name: {
                    required: "¡Upss! un nombre es requerido",
                    minlength: "¡Upss! un nombre contiene más de 3 caracteres"
                },
                lastname: {
                    required: "¡Upss! un apellido es requerido",
                    minlength: "¡Upss! un apellido contiene más de 3 caracteres"
                },
                email: {
                    required: "¡Upss! un email es requerido",
                    email: "¡Upss! escribe un email valido"
                },
                phone: {
                    required: "¡Upss! un telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                },
                fijo: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                document_type: {
                    required: "¡Upss! un tipo de documento es requerido",
                },
                estado_civil: {
                    required: "¡Upss! un estado civil es requerido",
                },
                numero_documento: {
                    required: "¡Upss! un numero de documento es requerido",
                    number: "¡Upss! este campo solo es numérico"
                },
                address: {
                    required: "¡Upss! una dirección es requerida",
                },
                city: {
                    required: "¡Upss! una ciudad es requerida",
                },
                country_id: {
                    required: "¡Upss! un país es requerido",
                },
                state_id: {
                    required: "¡Upss! un departamento es requerido",
                },
                date: {
                    required: "¡Upss! una fecha de nacimiento es requerido",
                    min: "¡Upss! Debe ser mayor de edad",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"
                },
                ////////////////////////////////////////////
                bfirstname1: {
                    required: "¡Upss! un nombre es requerido",
                    minlength: "¡Upss! un nombre contiene más de 3 caracteres"
                },
                bflastname1: {
                    required: "¡Upss! un apellido es requerido",
                    minlength: "¡Upss! un apellido contiene más de 3 caracteres"
                },
                bfemail1: {
                    required: "¡Upss! un email es requerido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone1: {
                    required: "¡Upss! un telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos",
                },
                bffijo1: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                bfparentesco1: {
                    required: "¡Upss! un parentesco de documento es requerido",
                },
                bfdocument1: {
                    required: "¡Upss! un tipo de documento es requerido",
                },
                bfnumero_documento1: {
                    required: "¡Upss! un numero de documento es requerido",
                    number: "¡Upss! este campo solo es numérico"
                },
                bfaddress1: {
                    required: "¡Upss! una dirección es requerida",
                },
                bfcity1: {
                    required: "¡Upss! una ciudad es requerida",
                },
                bfcountry_id1: {
                    required: "¡Upss! un país es requerido",
                },
                bfdeparment1: {
                    required: "¡Upss! un departamento es requerido",
                },
                bfdate1: {
                    required: "¡Upss! una fecha de nacimiento es requerido",
                },
                ////////////////////////////////////////////
                bfirstname2: {
                    required: "¡Upss! un nombre es requerido",
                    minlength: "¡Upss! un nombre contiene más de 3 caracteres"
                },
                bflastname2: {
                    required: "¡Upss! un apellido es requerido",
                    minlength: "¡Upss! un apellido contiene más de 3 caracteres"
                },
                bfemail2: {
                    required: "¡Upss! un email es requerido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone2: {
                    required: "¡Upss! un telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos",
                },
                bffijo2: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                bfparentesco2: {
                    required: "¡Upss! un parentesco de documento es requerido",
                },
                bfdocument2: {
                    required: "¡Upss! un tipo de documento es requerido",
                },
                bfnumero_documento2: {
                    required: "¡Upss! un numero de documento es requerido",
                    number: "¡Upss! este campo solo es numérico"
                },
                bfaddress2: {
                    required: "¡Upss! una dirección es requerida",
                },
                bfcity2: {
                    required: "¡Upss! una ciudad es requerida",
                },
                bfcountry_id2: {
                    required: "¡Upss! un país es requerido",
                },
                bfdeparment2: {
                    required: "¡Upss! un departamento es requerido",
                },
                bfdate2: {
                    required: "¡Upss! una fecha de nacimiento es requerido",
                },
                ////////////////////////////////////////////
                bfirstname3: {
                    required: "¡Upss! tu nombre es requerido",
                    minlength: "Un nombre contiene más de 3 caracteres"
                },
                bflastname3: {
                    required: "¡Upss! tu apellido es requerido",
                    minlength: "Un apellido contiene más de 3 caracteres"
                },
                bfemail3: {
                    required: "¡Upss! tu email es requerido",
                    email: "Escribe un email valido"
                },
                bfphone3: {
                    required: "¡Upss! tu telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos",
                },
                bffijo3: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                bfparentesco3: {
                    required: "¡Upss! un parentesco de documento es requerido",
                },
                bfdocument3: {
                    required: "¡Upss! tu tipo de documento es requerido",
                },
                bfnumero_documento3: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "Este campo solo es numérico"
                },
                bfaddress3: {
                    required: "¡Upss! tu dirección es requerido",
                },
                bfcity3: {
                    required: "¡Upss! tu ciudad es requerido",
                },
                bfcountry_id3: {
                    required: "Este campo es requerido",
                },
                bfdeparment3: {
                    required: "¡Upss! tu departamento es requerido",
                },
                bfdate3: {
                    required: "¡Upss! tu fecha de nacimiento es requerido",
                    min: "¡Upss! Tienes que ser mayor de edad",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"
                },
                ////////////////////////////////////////////
                bfirstname4: {
                    required: "¡Upss! tu nombre es requerido",
                    minlength: "Un nombre contiene más de 3 caracteres"
                },
                bflastname4: {
                    required: "¡Upss! tu apellido es requerido",
                    minlength: "Un apellido contiene más de 3 caracteres"
                },
                bfemail4: {
                    required: "¡Upss! tu email es requerido",
                    email: "Escribe un email valido"
                },
                bfphone4: {
                    required: "¡Upss! tu telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos",
                },
                bffijo4: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                bfparentesco4: {
                    required: "¡Upss! un parentesco de documento es requerido",
                },
                bfdocument4: {
                    required: "¡Upss! tu tipo de documento es requerido",
                },
                bfnumero_documento4: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "Este campo solo es numérico"
                },
                bfaddress4: {
                    required: "¡Upss! tu dirección es requerido",
                },
                bfcity4: {
                    required: "¡Upss! tu ciudad es requerido",
                },
                bfcountry_id4: {
                    required: "Este campo es requerido",
                },
                bfdeparment4: {
                    required: "¡Upss! tu departamento es requerido",
                },
                bfdate4: {
                    required: "¡Upss! tu fecha de nacimiento es requerido",
                    min: "¡Upss! Tienes que ser mayor de edad",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"
                },
                ////////////////////////////////////////////
                bfirstname5: {
                    required: "¡Upss! tu nombre es requerido",
                    minlength: "Un nombre contiene más de 3 caracteres"
                },
                bflastname5: {
                    required: "¡Upss! tu apellido es requerido",
                    minlength: "Un apellido contiene más de 3 caracteres"
                },
                bfemail5: {
                    required: "¡Upss! tu email es requerido",
                    email: "Escribe un email valido"
                },
                bfphone5: {
                    required: "¡Upss! tu telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos",
                },
                bffijo5: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                bfparentesco5: {
                    required: "¡Upss! un parentesco de documento es requerido",
                },
                bfdocument5: {
                    required: "¡Upss! tu tipo de documento es requerido",
                },
                bfnumero_documento5: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "Este campo solo es numérico"
                },
                bfaddress5: {
                    required: "¡Upss! tu dirección es requerido",
                },
                bfcity5: {
                    required: "¡Upss! tu ciudad es requerido",
                },
                bfcountry_id5: {
                    required: "Este campo es requerido",
                },
                bfdeparment5: {
                    required: "¡Upss! tu departamento es requerido",
                },
                bfdate5: {
                    required: "¡Upss! tu fecha de nacimiento es requerido",
                    min: "¡Upss! Tienes que ser mayor de edad",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"

                },
                ////////////////////////////////////////////
                bfirstname6: {
                    required: "¡Upss! tu nombre es requerido",
                    minlength: "Un nombre contiene más de 3 caracteres"
                },
                bflastname6: {
                    required: "¡Upss! tu apellido es requerido",
                    minlength: "Un apellido contiene más de 3 caracteres"
                },
                bfemail6: {
                    required: "¡Upss! tu email es requerido",
                    email: "Escribe un email valido"
                },
                bfphone6: {
                    required: "¡Upss! tu telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos"
                },
                bffijo6: {
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 7 digitos",
                    maxlength: "¡Upss! debe tener 7 digitos"
                },
                bfparentesco6: {
                    required: "¡Upss! un parentesco de documento es requerido",
                },
                bfdocument6: {
                    required: "¡Upss! tu tipo de documento es requerido",
                },
                bfnumero_documento6: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "Este campo solo es numérico"
                },
                bfaddress6: {
                    required: "¡Upss! tu dirección es requerido",
                },
                bfcity6: {
                    required: "¡Upss! tu ciudad es requerido",
                },
                bfcountry_id6: {
                    required: "Este campo es requerido",
                },
                bfdeparment6: {
                    required: "¡Upss! tu departamento es requerido",
                },
                bfdate6: {
                    required: "¡Upss! tu fecha de nacimiento es requerido",
                    min: "¡Upss! Tienes que ser mayor de edad",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"
                },
            }
        });

});




/*
odoo.define('web_sale_extended.payment_method_process', function(require) {
    'use strict';
    
    $(function() {
        $('#payment_method_tabs').tabs();
    });
});
*/

odoo.define('web_sale_extended.welcome_masmedicos', function(require) {
    'use strict';
    
    $(function() {
        $('#poliza_download_btn').on('click', function() {
            let order_id = $("input[name='order_id']").val();
            var route= '/report/pdf/web_sale_extended.report_customreport_customeasytek_template/'
            var url = route + order_id;
            window.location.href = url;
        });
    });
});






odoo.define('web_sale_extended.payment_process', function(require) {
    'use strict';

    $(function() {
        $('#credit_card_country_id').selectpicker();
        $('#credit_card_state_id').selectpicker();
        $('#credit_card_city').selectpicker();
        
        $('#pse_country_id').selectpicker();
        $('#pse_state_id').selectpicker('val', '');
        $('#pse_city').selectpicker();
        
        $('#cash_country_id').selectpicker();
        $('#cash_state_id').selectpicker();
        $('#cash_city').selectpicker();
        
        $('#submit_beneficiaries_add').on('click', function() {
            let order_id = $("input[name='order_id']").val();
            var route = '/my/order/beneficiaries/'
            var url = route + order_id;
            window.location.href = url;
        });
        
        
        $('#submit_payment_rejected').on('click', function() {
            var url = '/shop/payment'
            window.location.href = url;
        });
        
        $('#submit_pse_payment_process').on('click', function() {
            var url = '/shop/payment'
            window.location.href = url;
        });
        
        
        //$('#payment_btn_cash').on('click', function() {
        //    alert('payulatam-payment-form-cash');
        //    $('#payulatam-payment-form-cash').attr('action', '/shop/payment/payulatam-gateway-api/cash_process');
        //    $('#payulatam-payment-form-cash').submit();
        //});
        function consultarZipcodeCreditCard(ciudad){
            $.ajax({
                data: { 'city_id': ciudad },
                url: "/search/zipcodes",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    document.querySelector("input[name='credit_card_zip']").value = decode_data['data'].zipcode;
                    document.querySelector("input[name='credit_card_zip_id']").value = decode_data['data'].zipid;
                }
            });
        }
        function consultarZipcodePSE(ciudad){
            $.ajax({
                data: { 'city_id': ciudad },
                url: "/search/zipcodes",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    document.querySelector("input[name='pse_zip']").value = decode_data['data'].zipcode;
                    document.querySelector("input[name='pse_zip_id']").value = decode_data['data'].zipid;
                }
            });
        }
        function consultarZipcodeCash(ciudad){
            $.ajax({
                data: { 'city_id': ciudad },
                url: "/search/zipcodes",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    document.querySelector("input[name='cash_zip']").value = decode_data['data'].zipcode;
                    document.querySelector("input[name='cash_zip_id']").value = decode_data['data'].zipid;
                }
            });
        }
        
        $('#credit_card_city').change(function() {
            let data_select = $("#credit_card_city option:selected").val();
            consultarZipcodeCreditCard(data_select);
        });
        $('#pse_city').change(function() {
            let data_select = $("#pse_city option:selected").val();
            consultarZipcodePSE(data_select);
        });
        $('#cash_city').change(function() {
            let data_select = $("#cash_city option:selected").val();
            consultarZipcodeCash(data_select);
        });
        
        function consultarCiudadesCreditCard(estado, elemento) {
            $.ajax({
                data: { 'departamento': estado },
                url: "/search/cities",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    let elemento_completo = $(elemento);
                    $('#credit_card_city').selectpicker('destroy');
                    $('#credit_card_city').empty();
                    decode_data.data.cities.forEach(function(obj) {
                        $('#credit_card_city').append($("<option></option>")
                            .attr("value", obj.city_id).text(obj.city));
                    });
                    $('#credit_card_city').selectpicker();
                    let data_select = $("#credit_card_city option:selected").val();
                    consultarZipcodeCreditCard(data_select);
                }
            });
        }
        function consultarCiudadesPSE(estado, elemento) {
            $.ajax({
                data: { 'departamento': estado },
                url: "/search/cities",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    let elemento_completo = $(elemento);
                    $('#pse_city').selectpicker('destroy');
                    $('#pse_city').empty();
                    decode_data.data.cities.forEach(function(obj) {
                        $('#pse_city').append($("<option></option>")
                            .attr("value", obj.city_id).text(obj.city));
                    });
                    $('#pse_city').selectpicker();
                    let data_select = $("#pse_city option:selected").val();
                    consultarZipcodePSE(data_select);
                }
            });
        }
        function consultarCiudadesCash(estado, elemento) {
            $.ajax({
                data: { 'departamento': estado },
                url: "/search/cities",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    let elemento_completo = $(elemento);
                    $('#cash_city').selectpicker('destroy');
                    $('#cash_city').empty();
                    decode_data.data.cities.forEach(function(obj) {
                        $('#cash_city').append($("<option></option>")
                            .attr("value", obj.city_id).text(obj.city));
                    });
                    $('#pse_city').selectpicker();
                    let data_select = $("#cash_city option:selected").val();
                    consultarZipcodeCash(data_select);
                }
            });
        }
        
        $("select[name='credit_card_state_id']").on('change', function cambiarEstado() {
            let estado = $(this).val();
            let elemento = "select[name='credit_card_city']";
            if (estado != ''){
                consultarCiudadesCreditCard(estado, elemento);
            } else {
                $('#credit_card_city').selectpicker('destroy');
                $('#credit_card_city').empty();
                $('#credit_card_city').append($("<option></option>")
                            .attr("value", '').text('Ciudad...'));
                $('#credit_card_city').selectpicker();
            }
        });
        $("select[name='pse_state_id']").on('change', function cambiarEstado() {
            let estado = $(this).val();
            let elemento = "select[name='pse_city']";
            if (estado != ''){
                consultarCiudadesPSE(estado, elemento);
            } else {
                $('#pse_city').selectpicker('destroy');
                $('#pse_city').empty();
                $('#pse_city').append($("<option></option>")
                            .attr("value", '').text('Ciudad...'));
                $('#pse_city').selectpicker();
            }
        });
        $("select[name='cash_state_id']").on('change', function cambiarEstado() {
            let estado = $(this).val();
            let elemento = "select[name='cash_city']";
            if (estado != ''){
                consultarCiudadesCash(estado, elemento);
            } else {
                $('#cash_city').selectpicker('destroy');
                $('#cash_city').empty();
                $('#cash_city').append($("<option></option>")
                            .attr("value", '').text('Ciudad...'));
                $('#cash_city').selectpicker();
            }
        });
        
        var partner_country_id = $("input[name='partner_country_id']").val();
        var partner_state_id = $("input[name='partner_state_id']").val();
        var partner_city_id = $("input[name='partner_city_id']").val();
        //$("input[select='partner_country_id'] option:selected").val(partner_country_id);
        $("select[name='credit_card_country_id']").val(partner_country_id);
        $("select[name='credit_card_state_id']").val(partner_state_id);
        $("select[name='credit_card_city_id']").val(partner_state_id);
        $("select[name='pse_country_id']").val(partner_country_id);
        $("select[name='pse_state_id']").val(partner_state_id);
        $("select[name='pse_city_id']").val(partner_state_id);
        $("select[name='cash_country_id']").val(partner_country_id);
        $("select[name='cash_state_id']").val(partner_state_id);
        $("select[name='cash_city_id']").val(partner_state_id);
        $('#credit_card_country_id').selectpicker('refresh')
        $('#credit_card_state_id').selectpicker('refresh')
        $('#credit_card_city_id').selectpicker('refresh')
        $('#pse_country_id').selectpicker('refresh')
        $('#pse_state_id').selectpicker('refresh')
        $('#pse_city_id').selectpicker('refresh')
        $('#cash_country_id').selectpicker('refresh')
        $('#cash_state_id').selectpicker('refresh')
        $('#cash_city_id').selectpicker('refresh')
        
        var credit_city = "select[name='credit_card_city']";
        consultarCiudadesCreditCard(partner_state_id, credit_city);
        var pse_city = "select[name='pse_city']";
        consultarCiudadesPSE(partner_state_id, pse_city);
        var cash_city = "select[name='cash_city']";
        consultarCiudadesCash(partner_state_id, cash_city);
       
        $.validator.addMethod("creditCardfechaVencimiento", function (value, element) {
            var lastYear = new Date().getFullYear();
            var lastMonth = new Date.getMonth();
            var selectYear = "select[name='credit_card_due_year']".val();
            var selectMonth = "select[name='credit_card_due_month']".val()
            
            if (lastYear == selectYear){
                if (int(lastMonth) > int(selectMonth)){
                    return false;
                }
            }
            return true;
            
        }, "¡Upss! Fecha de Vencimiento Invalida");

        
        
        $("#payulatam-payment-form").validate({
            rules: {
                credit_card_number: {
                    required: true,
                    minlength: 13,
                    maxlength: 16,
                    number: true,
                },
                credit_card_code: {
                    required: true,
                    minlength: 3,
                    maxlength: 3,
                    number: true,
                },
                credit_card_name: {
                    required: true,
                    minlength: 3,
                    maxlength: 15,
                    lettersonly: true,
                },
                credit_card_billing_firstname: {
                    required: true,
                    lettersonly: true,
                },
                credit_card_billing_lastname: {
                    required: true,
                    lettersonly: true,
                },
                credit_card_billing_email: {
                    required: true,
                    email: true,
                },
                credit_card_partner_phone: {
                    required: true,
                    number: true,
                    formMovilFijoLength: true,
                },
                credit_card_partner_document: {
                    required: true,
                    number: true,
                },
                identification_document: {
                    required: true,
                    number: true,
                },
                credit_card_partner_street: {
                    required: true,
                },
                credit_card_city: {
                    required: true,
                },
                credit_card_country_id: {
                    required: true,
                },
                credit_card_state_id: {
                    required: true,
                },
                cash_billing_firstname: {
                    required: true,
                    lettersonly: true,
                },
                cash_card_billing_lastname: {
                    required: true,
                    lettersonly: true,
                },
            },
            messages: {
                credit_card_number: {
                    required: "¡Upss! tu número de tarjeta es requerido",
                    minlength: "¡Upss! debe contener entre 13y 16 digitos",
                    maxlength: "¡Upss! debe contener entre 13y 16 digitos"
                },
                credit_card_code: {
                    required: "¡Upss! el código de seguridad es requerido",
                    maxlength: "¡Upss! máximo 4 digitos"
                },
                credit_card_name: {
                    required: "¡Upss! el nombre de tajeta es requerido",
                    minlength: "¡Upss! debe contener 3 o más caracteres",
                    maxlength: "¡Upss! debe contener máximo 15 caracteres",
                    lettersonly: "¡Upss! debe contener solo letras"
                },
                credit_card_partner_phone: {
                    required: "¡Upss! tu telefono es requerido",
                    number: "¡Upss! este campo solo es numérico",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos"

                },
                credit_card_billing_email: {
                    email: "¡Upss! debe registrar un correo valido",
                },
                credit_card_billing_firstname: {
                    required: "¡Upss! tu(s) nombre(s) es requerido",
                },
                credit_card_billing_lastname: {
                    required: "¡Upss! tu(s) apellido(s) es requerido",
                },
                credit_card_partner_document: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "¡Upss! este campo solo es numérico"
                },
                identification_document: {
                    required: "¡Upss! tu numero de documento es requerido",
                    number: "¡Upss! este campo solo es numérico"
                },
                credit_card_partner_street: {
                    required: "¡Upss! tu dirección es requerida",
                },
                credit_card_city: {
                    required: "¡Upss! tu ciudad es requerida",
                },
                credit_card_country_id: {
                    required: "¡Upss! tu país es requerido",
                },
                credit_card_state_id: {
                    required: "¡Upss! tu departamento es requerido",
                },
                cash_billing_firstname: {
                    required: "¡Upss! tu(s) nombre(s) es requerido",
                },
                cash_billing_lastname: {
                    required: "¡Upss! tu(s) apellido(s) es requerido",
                },
            }
        });

        $("#payulatam-payment-form-cash").validate({
            rules: {
                cash_billing_firstname: {
                    required: true,
                    lettersonly: true,
                },
                cash_card_billing_lastname: {
                    required: true,
                    lettersonly: true,
                },
                cash_partner_document: {
                    required: true,
                    number: true,
                },
                cash_billing_email: {
                    required: true,
                    email: true,
                },
                cash_partner_street: {
                    required: true,
                },
            },
            messages: {
                cash_billing_firstname: {
                    required: "¡Upss! tu(s) nombre(s) es requerido",
                    lettersonly: "¡Upss! debe contener solo letras"
                },
                cash_billing_lastname: {
                    required: "¡Upss! tu(s) apellido(s) es requerido",
                    lettersonly: "¡Upss! debe contener solo letras"
                },
                cash_partner_document: {
                    required: "¡Upss! tu No. de documento es requerido",
                    number: "¡Upss! debe contener solo números"
                },
                cash_billing_email: {
                    required: "¡Upss! tu email es requerido",
                    email: "¡Upss! debe contener un correo valido"
                },
                cash_partner_street: {
                    required: "¡Upss! tu documento es requerido",
                },
            }
        });
        

        $("#payulatam-payment-form-pse").validate({
            rules: {
                pse_owner: {
                    required: true,
                    lettersonly: true,
                },
                pse_billing_firstname: {
                    required: true,
                    lettersonly: true,
                },
                pse_card_billing_lastname: {
                    required: true,
                    lettersonly: true,
                },
                pse_partner_document: {
                    required: true,
                    number: true,
                },
                pse_billing_email: {
                    required: true,
                    email: true,
                },
                pse_partner_street: {
                    required: true,
                },
            },
            messages: {
                pse_owner: {
                    required: "¡Upss! el titular de la cuenta es requerido",
                    lettersonly: "¡Upss! debe contener solo letras"
                },
                pse_billing_firstname: {
                    required: "¡Upss! tu(s) nombre(s) es requerido",
                    lettersonly: "¡Upss! debe contener solo letras"
                },
                pse_billing_lastname: {
                    required: "¡Upss! tu(s) apellido(s) es requerido",
                    lettersonly: "¡Upss! debe contener solo letras"
                },
                pse_partner_document: {
                    required: "¡Upss! tu No. de documento es requerido",
                    number: "¡Upss! debe contener solo números"
                },
                pse_billing_email: {
                    required: "¡Upss! tu email es requerido",
                    email: "¡Upss! debe contener un correo valido"
                },
                pse_partner_street: {
                    required: "¡Upss! tu documento es requerido",
                },
            }
        });
        
        var bank_url = $("#bank_url").val();
        var url_payment_receipt_pdf = $("#url_payment_receipt_pdf").val();
        if (bank_url) {
            window.open(bank_url);
        }
        if (url_payment_receipt_pdf) {
            window.open(url_payment_receipt_pdf);
        }
    });
   
});

 
