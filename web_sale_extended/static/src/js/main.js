$('.product_image .img').css('max-width','220px');
$('.product_image .img').css('max-height','123');
$('#submit_beneficiaries').css('margin-top','-220px');

odoo.define('web_sale_extended.show_website_cities', function(require) {
    'use strict';

    $(function() {
        $('#country_address_id').selectpicker();
        $('#state_address_id').selectpicker('val', '');
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
        
        function consultarPhoneCode(pais){
            $.ajax({
                data: { 'id': pais },
                url: "/search/phonecode",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    let phone = document.querySelector("input[name='phone']").value;
                    phone = phone.split(')');
                    let number = phone[phone.length - 1].trim();
                    document.querySelector("input[name='phone']").value = '(+' + decode_data['data'].phonecode + ') ' + number;    
                }
            });
        }
        
        function consultarEstados(pais) {
            $.ajax({
                data: { 'id': pais },
                url: "/search/states",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);                    
                    $('#state_address_id').selectpicker('destroy');
                    $('#state_address_id').empty();
                    $('#city').selectpicker('destroy');
                    $('#city').empty();
                    decode_data.data.states.forEach(function(obj) {
                        $('#state_address_id').append($("<option></option>")
                            .attr("value", obj.state_id).text(obj.state));
                    });
                    let estado = $('#state_address_id').val();
                    let elemento = "select[name='city']";
                    consultarCiudades(estado, elemento);
                    $('#state_address_id').selectpicker('render');
                    $('#city').selectpicker('render');
                    
                }
            });
        }

        $('#city').change(function() {
            let data_select = $("#city option:selected").val();
            let country = $("#country_address_id option:selected").val();
            if(country == 49){
                consultarZipcode(data_select);
            }
            
        });
        
        $('.div_state_text').hide();
        $('.div_city_text').hide();
        
        consultarPhoneCode($("#country_address_id option:selected").val());
        consultarEstados($("#country_address_id option:selected").val());
        
        $('#country_address_id').change(function() {
            let data_select = $("#country_address_id option:selected").val();            
            consultarPhoneCode(data_select);
            if (data_select != 49){  
                document.querySelector("input[name='zip']").value = "";
                document.querySelector("input[name='zip_id']").value = "";
                $('.div_state').hide();
                $('.div_city').hide();
                $('.div_state_text').show();
                $('.div_city_text').show();
            }
            else{ 
                consultarEstados(data_select);                
                $('.div_state_text').hide();
                $('.div_city_text').hide();
                $('.div_state').show();
                $('.div_city').show();   
            }
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

        $("select[name='state_address_id']").on('change', function cambiarEstado() {
            let estado = $(this).val();
            let elemento = "select[name='city']";
            let country = $("#country_address_id option:selected").val();
            if (country == 49){
                consultarCiudades(estado, elemento);
            } else {
                $('#city').selectpicker('destroy');
                $('#city').empty();
                $('#city').append($("<option></option>")
                            .attr("value", '').text('Ciudad...'));
                $('#city').selectpicker();
            }
        });
        
        var partner_id = $("input[name='partner_id']").val();
        var partner_country_id = $("input[name='partner_country_id']").val();
        var partner_state_id = $("input[name='partner_state_id']").val();
        var partner_city_id = $("input[name='partner_city_id']").val();
        var partner_document_type = $("input[name='partner_document_type']").val();
        if (parseInt(partner_id) > 0 && parseInt(partner_city_id) > 0){
            $("select[name='state_id']").val(partner_state_id)
            $("select[name='document']").val(partner_document_type)
            $('#state_address_id').selectpicker('refresh')
            $('#document').selectpicker('refresh')
            consultarCiudades(partner_state_id, partner_city_id);
        }

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
                $("input[name='bffijo1']").val(telefono_fijo_asegurador);
            }
        });
        
        $("input[name='bfdate2']").on('change', function calcularEdad() {
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
                $("input[name='bfemail2']").val(email_asegurador);
                $("input[name='bfaddress2']").val(adress_asegurador);
                $("input[name='bffijo2']").val(telefono_fijo_asegurador);
            }
        });
        
        
        $("input[name='bfdate3']").on('change', function calcularEdad() {
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
                $("input[name='bfemail3']").val(email_asegurador);
                $("input[name='bfaddress3']").val(adress_asegurador);
                $("input[name='bffijo3']").val(telefono_fijo_asegurador);
            }
        });
        
        
        $("input[name='bfdate4']").on('change', function calcularEdad() {
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
                $("input[name='bfemail4']").val(email_asegurador);
                $("input[name='bfaddress4']").val(adress_asegurador);
                $("input[name='bffijo4']").val(telefono_fijo_asegurador);
            }
        });
        
        
        $("input[name='bfdate5']").on('change', function calcularEdad() {
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
                $("input[name='bfemail5']").val(email_asegurador);
                $("input[name='bfaddress5']").val(adress_asegurador);
                $("input[name='bffijo5']").val(telefono_fijo_asegurador);
            }
        });
        
        
        $("input[name='bfdate6']").on('change', function calcularEdad() {
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
                $("input[name='bfemail6']").val(email_asegurador);
                $("input[name='bfaddress6']").val(adress_asegurador);
                $("input[name='bffijo6']").val(telefono_fijo_asegurador);
            }
        });
        
        $.validator.addMethod("formMovilFijoLength", function (value, element) {
            let number = element.value;
            number = number.split(')');
            number = number[number.length - 1].trim();
           if(number.length == 7 || number.length == 10){
              return true;
           } else {
              return false;
           }
        }, "¡Upss! debe tener 7 ó 10 digitos");


        $.validator.addMethod("lettersonly", function(value, element) {
            //return this.optional(element) || /^[a-zA-ZÀ-ÿ\u00f1\u00d1]+(\s*[a-zA-ZÀ-ÿ\u00f1\u00d1]*)*[a-zA-ZÀ-ÿ\u00f1\u00d1]+$/g.test(value);
            return this.optional(element) || /^[a-zA-ZÀ-ÿ\u00f1\u00d1]+(\s*[a-zA-ZÀ-ÿ\u00f1\u00d1]*)*[a-zA-ZÀ-ÿ\u00f1\u00d1]+$/g.test(value.replace(/^\s+|\s+$/g, ''));
        }, "¡Upss! deben ser ser solo letras");
        
        $.validator.addMethod("lettersnumberonly", function(value, element) {
            var document = $("select[name='document']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            }
            return this.optional(element) || /^[0-9]*$/.test(value);
        }, "¡Upss! deben ser ser solo letras");
        
        $.validator.addMethod("documentrange", function(value, element) {
            var document = $("select[name='document']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
        
        $.validator.addMethod("email2", function(value, element) {
            return this.optional(element) || /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i.test(value);
        }, "¡Upss! deben contener caracteres validos");

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
                    email2: true
                },
                phone: {
                    required: true,
                    formMovilFijoLength: true,
                },
                document: {
                    required: true,
                },
                identification_document: {
                    required: true,
                    lettersnumberonly: true,
                    documentrange: true,
                    /*
                    min: {
                        depends: function(elem) {
                            var document = $("select[name='document']").val();
                            var identification_document = $("input[name='identification_document']").val();
                            var number = /^[0-9\s]/g;
                            var numberletter= /^[A-Za-z0-9]/g;
                            console.log(document);
                            console.log(identification_document);
                            if (document == '7') { //pasaporte
                                if (/^[A-Za-z0-9]/g.test(identification_document)) {
                                    console.log('ingresando');
                                    return true;
                                }
                                console.log(numberletter.test(identification_document));
                                return false;
                            } else {
                                if (number.test(identification_document) == true) {
                                    return true;
                                }
                                return false;
                            }
                        }
                    },*/
                },
                street: {
                    required: true,
                    minlength: 3,
                    maxlength: 100,
                },
                city: {
                    required: true,
                },
                country_address_id: {
                    required: true,
                },
                state_address_id: {
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='expedition_date']").val();
                            let expedition_date = new Date(fecha);
                            let hoy = new Date();
                            if (expedition_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) {
                            let birthdate_date_form = $("input[name='birthdate_date']").val();
                            let expedition_date_form = $("input[name='expedition_date']").val();
                            let birthdate_date = new Date(birthdate_date_form);
                            let expedition_date = new Date(expedition_date_form);
                            let hoy = new Date();
                            if (expedition_date <= birthdate_date) {
                                return true;
                            }
                        }
                    }
                }
            },
            messages: {
                name: {
                    required: "¡Upss! tu nombre es requerido",
                    minlength: "Upss! Un nombre contiene más de 3 caracteres"
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
                    email: "¡Upss! escribe un email valido",
                    email2: "¡Upss! escribe un email valido"
                },
                phone: {
                    required: "¡Upss! tu telefono es requerido",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos"
                },
                document: {
                    required: "¡Upss! tu tipo de documento es requerido",
                    
                },
                identification_document: {
                    required: "¡Upss! tu numero de documento es requerido",
                    lettersnumberonly: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange: "¡Upss! cantidad de digitos no es correcto",
                },
                street: {
                    required: "¡Upss! tu dirección es requerida",
                    minlength: "¡Upss! una dirección contiene más de 3 caracteres",
                    maxlength: "¡Upss! tu dirección no puede tener más de 100 caracteres",
                },
                city: {
                    required: "¡Upss! tu ciudad es requerida",

                },
                country_address_id: {
                    required: "¡Upss! tu país es requerido",
                },
                state_address_id: {
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
                    min: "¡Upss! fecha invalida",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"

                },
                expedition_date: {
                    required: "¡Upss! tu fecha de expedición es requerido",
                    min: "¡Upss! debe ser superior a la fecha de nacimiento",
                    max: "¡Upss! debe ser igual o inferior a la fecha actual"
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
    
    
     function llenar(){
        let beneficiary_number = parseInt($("#beneficiaries_number").val());
        for(let i = 1; i <= beneficiary_number; i++){
            $('#cant_beneficiarios').append($("<option></option>").attr("value", i).text(i));
        };
    }
    
    llenar();
    
        

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
                let elemento = "select[name='" + id_elemento + "']";
                let elemento_completo = $(elemento);
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
                let elemento = "select[name='" + id_elemento + "']";
                let elemento_completo = $(elemento);
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
                let elemento = "select[name='" + id_elemento + "']";
                let elemento_completo = $(elemento);
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
        console.log('4');
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
                    } else if (item == 6) {
                        $('#bfcity6').empty();
                        decode_data.data.cities.forEach(function(obj) {
                            $('#bfcity6').append($("<option></option>")
                                .attr("value", obj.city_id).text(obj.city));
                        });
                    }
                    
                }
            });
        }
    
    function obtenerInfoComprador(order_id){
            $.ajax({
                data: { 'order_id': order_id },
                url: "/search/buyer/info",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);
                    if(decode_data['data'].country_id == 49){
                        document.querySelector("input[name='name']").value = decode_data['data'].firstname;
                        $("input[name='name']").prop('readonly', true);
                        document.querySelector("input[name='othername']").value = decode_data['data'].othernames;
                        $("input[name='othername']").prop('readonly', true);
                        document.querySelector("input[name='lastname']").value = decode_data['data'].lastname;
                        $("input[name='lastname']").prop('readonly', true);
                        document.querySelector("input[name='lastname2']").value = decode_data['data'].lastname2;    
                        $("input[name='lastname2']").prop('readonly', true);                    
                        document.querySelector("input[name='numero_documento']").value = decode_data['data'].identification_document;
                        $("input[name='numero_documento']").prop('readonly', true);
                        document.querySelector("input[name='expedition_date']").value = decode_data['data'].expedition_date;
                        $("input[name='expedition_date']").prop('disabled', true);  
                        document.querySelector("input[name='email']").value = decode_data['data'].email;
                        $("input[name='email']").prop('readonly', true); 
                        document.querySelector("input[name='phone']").value = decode_data['data'].phone;
                        $("input[name='phone']").prop('readonly', true); 
                        document.querySelector("input[name='address']").value = decode_data['data'].address;
                        $("input[name='address']").prop('readonly', true); 
                        document.querySelector("input[name='date']").value = decode_data['data'].birthdate_date;    
                        $("input[name='date']").prop('disabled', true); 
                        $("#document_type").val(String(decode_data['data'].document_type_id)).change();
                        $("#document_type").prop('disabled', true); 
                        $("#bfdeparment0").prop('disabled', true); 
                        $("#bfcity0").prop('disabled', true); 
                        $("#bfdeparment0").val(String(decode_data['data'].state_id)).change();
                        setTimeout(() => { $("#bfcity0").val(String(decode_data['data'].city_id)).change(); }, 500);
                    }
                    else{
                        $('#flexCheckDefault').val('0');
                        $('#div_error').show();
                        $("#flexCheckDefault").prop("checked", false);
                        $("#flexCheckDefault").attr("disabled", true);
                    }
                                   
                }
            });
        }
    
    
    $('#flexCheckDefault').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $(this).val('1');
            let url = window.location.href.split("/");
            let number = url[url.length - 1];
            obtenerInfoComprador(number);
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            document.querySelector("input[name='name']").value = "";
            document.querySelector("input[name='othername']").value = "";
            document.querySelector("input[name='lastname']").value = "";
            document.querySelector("input[name='lastname2']").value = "";
            document.querySelector("select[name='document_type']").value = "";
            document.querySelector("input[name='numero_documento']").value = "";
            document.querySelector("input[name='expedition_date']").value = "";
            document.querySelector("input[name='email']").value = "";
            document.querySelector("input[name='phone']").value = "";
            document.querySelector("input[name='address']").value = "";
            document.querySelector("input[name='date']").value = "";
            $('#bfdeparment0').val('');
            $('#bfcity0').val('');
            $(this).val('0');

            $("input[name='name']").prop('readonly', false);           
            $("input[name='othername']").prop('readonly', false);            
            $("input[name='lastname']").prop('readonly', false);           
            $("input[name='lastname2']").prop('readonly', false); 
            $("input[name='numero_documento']").prop('readonly', false); 
            $("input[name='expedition_date']").prop('disabled', false);  
            $("input[name='email']").prop('readonly', false); 
            $("input[name='phone']").prop('readonly', false); 
            $("input[name='address']").prop('readonly', false); 
            $("input[name='date']").prop('disabled', false);     
            $("#document_type").prop('disabled', false); 
            $("#bfdeparment0").prop('disabled', false); 
            $("#bfcity0").prop('disabled', false); 
        }
    });
    
    
    $('#bfCheckBox1').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $("input[name='bfaddress1']").val($("input[name='address']").val());
            $("select[name='bfdeparment1']").val($("select[name='deparment']").val()).change();            
            setTimeout(() => { $("select[name='bfcity1']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo1']").val($("input[name='fijo']").val());
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            $("input[name='bfaddress1']").val('');
            $("select[name='bfdeparment1']").val('');
            $("select[name='bfcity1']").val('');
        }
    });
    
    $('#bfCheckBox2').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $("input[name='bfaddress2']").val($("input[name='address']").val());
            $("select[name='bfdeparment2']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity2']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo2']").val($("input[name='fijo']").val());
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            $("input[name='bfaddress2']").val('');
            $("select[name='bfdeparment2']").val('');
            $("select[name='bfcity2']").val('');
        }
    });
    
    $('#bfCheckBox3').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $("input[name='bfaddress3']").val($("input[name='address']").val());
            $("select[name='bfdeparment3']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity3']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo3']").val($("input[name='fijo']").val());
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            $("input[name='bfaddress3']").val('');
            $("select[name='bfdeparment3']").val('');
            $("select[name='bfcity3']").val('');
        }
    });
    
    $('#bfCheckBox4').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $("input[name='bfaddress4']").val($("input[name='address']").val());
            $("select[name='bfdeparment4']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity4']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo4']").val($("input[name='fijo']").val());
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            $("input[name='bfaddress4']").val('');
            $("select[name='bfdeparment4']").val('');
            $("select[name='bfcity4']").val('');
        }
    });
    
    $('#bfCheckBox5').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $("input[name='bfaddress5']").val($("input[name='address']").val());
            $("select[name='bfdeparment5']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity5']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo5']").val($("input[name='fijo']").val());
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            $("input[name='bfaddress5']").val('');
            $("select[name='bfdeparment5']").val('');
            $("select[name='bfcity5']").val('');
        }
    });
    
    $('#bfCheckBox6').on('click', function() {
        if( $(this).is(':checked') ){
            // Hacer algo si el checkbox ha sido seleccionado
            $("input[name='bfaddress6']").val($("input[name='address']").val());
            $("select[name='bfdeparment6']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity6']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo6']").val($("input[name='fijo']").val());
        } else {
            // Hacer algo si el checkbox ha sido deseleccionado
            $("input[name='bfaddress6']").val('');
            $("select[name='bfdeparment6']").val('');
            $("select[name='bfcity6']").val('');
        }
    });
    
//     $('#submit_beneficiaries').on('click', function() {
//         if( $('#bfCheckBox1').is(':checked') ){
//             $("input[name='bfaddress1']").val($("input[name='address']").val());
//             $("select[name='bfdeparment1']").val($("select[name='deparment']").val()).change();
//             setTimeout(() => { $("select[name='bfcity1']").val($("select[name='city']").val()).change(); }, 500);
//             $("input[name='bffijo1']").val($("input[name='fijo']").val());
//         }
//         if( $('#bfCheckBox2').is(':checked') ){
//             $("input[name='bfaddress2']").val($("input[name='address']").val());
//             $("select[name='bfdeparment2']").val($("select[name='deparment']").val()).change();
//             setTimeout(() => { $("select[name='bfcity2']").val($("select[name='city']").val()).change(); }, 500);
//             $("input[name='bffijo2']").val($("input[name='fijo']").val());
//         }
//         if( $('#bfCheckBox3').is(':checked') ){
//             $("input[name='bfaddress3']").val($("input[name='address']").val());
//             $("select[name='bfdeparment3']").val($("select[name='deparment']").val()).change();
//             setTimeout(() => { $("select[name='bfcity3']").val($("select[name='city']").val()).change(); }, 500);
//             $("input[name='bffijo3']").val($("input[name='fijo']").val());
//         }
//         if( $('#bfCheckBox4').is(':checked') ){
//             $("input[name='bfaddress4']").val($("input[name='address']").val());
//             $("select[name='bfdeparment4']").val($("select[name='deparment']").val()).change();
//             setTimeout(() => { $("select[name='bfcity4']").val($("select[name='city']").val()).change(); }, 500);
//             $("input[name='bffijo4']").val($("input[name='fijo']").val());
//         }
//         if( $('#bfCheckBox5').is(':checked') ){
//             $("input[name='bfaddress5']").val($("input[name='address']").val());
//             $("select[name='bfdeparment5']").val($("select[name='deparment']").val()).change();
//             setTimeout(() => { $("select[name='bfcity5']").val($("select[name='city']").val()).change(); }, 500);
//             $("input[name='bffijo5']").val($("input[name='fijo']").val());
//         }
//         if( $('#bfCheckBox6').is(':checked') ){
//             $("input[name='bfaddress6']").val($("input[name='address']").val());
//             $("select[name='bfdeparment6']").val($("select[name='deparment']").val()).change();
//             setTimeout(() => { $("select[name='bfcity6']").val($("select[name='city']").val()).change(); }, 500);
//             $("input[name='bffijo6']").val($("input[name='fijo']").val());
//         }
//     });
    
    
   
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
    $("select[name='bfdeparment6']").on('change', function cambiarCiudades() {
        let estado = $(this).val();
        let elemento = "select[name='bfcity6']";
        consultarCiudadesBeneficiary(estado, elemento, 6);

    });

    $("#btn_terminos").click(function() {
        document.getElementById("politica").innerHTML = '';
        document.getElementById("terminos").innerHTML = '<embed src="/web_sale_extended/static/src/files/terminos.pdf" width="100%" height="680px">Acepto términos y condiciones</embed>';
        $("#terminos").toggle();
    });
    
    $("#btn_politica").click(function() {
        document.getElementById("terminos").innerHTML = '';
        document.getElementById("politica").innerHTML = '<embed src="/web_sale_extended/static/src/files/tratamiento_de_datos.pdf" width="100%" height="680px">Acepto política de tratamiento de datos</embed>';
        $("#politica").toggle();
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

    $("#submit_beneficiaries").on('click', function(event){
        event.preventDefault();
        if( $('#bfCheckBox1').is(':checked') ){
            $("input[name='bfaddress1']").val($("input[name='address']").val());
            $("select[name='bfdeparment1']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity1']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo1']").val($("input[name='fijo']").val());
        }
        if( $('#bfCheckBox2').is(':checked') ){
            $("input[name='bfaddress2']").val($("input[name='address']").val());
            $("select[name='bfdeparment2']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity2']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo2']").val($("input[name='fijo']").val());
        }
        if( $('#bfCheckBox3').is(':checked') ){
            $("input[name='bfaddress3']").val($("input[name='address']").val());
            $("select[name='bfdeparment3']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity3']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo3']").val($("input[name='fijo']").val());
        }
        if( $('#bfCheckBox4').is(':checked') ){
            $("input[name='bfaddress4']").val($("input[name='address']").val());
            $("select[name='bfdeparment4']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity4']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo4']").val($("input[name='fijo']").val());
        }
        if( $('#bfCheckBox5').is(':checked') ){
            $("input[name='bfaddress5']").val($("input[name='address']").val());
            $("select[name='bfdeparment5']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity5']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo5']").val($("input[name='fijo']").val());
        }
        if( $('#bfCheckBox6').is(':checked') ){
            $("input[name='bfaddress6']").val($("input[name='address']").val());
            $("select[name='bfdeparment6']").val($("select[name='deparment']").val()).change();
            setTimeout(() => { $("select[name='bfcity6']").val($("select[name='city']").val()).change(); }, 500);
            $("input[name='bffijo6']").val($("input[name='fijo']").val());
        }
        $('#beneficiary').submit();
        
    });


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
        let number = element.value;
            number = number.split(')');
            number = number[number.length - 1].trim();
        if(number.length == 7 || number.length == 10){
            return true;
        } else {
            return false;
        }
    }, "¡Upss! debe tener 7 ó 10 digitos");

    $.validator.addMethod("lettersonly", function(value, element) {
        return this.optional(element) || /^[a-zA-ZÀ-ÿ\u00f1\u00d1]+(\s*[a-zA-ZÀ-ÿ\u00f1\u00d1]*)*[a-zA-ZÀ-ÿ\u00f1\u00d1]+$/g.test(value.replace(/^\s+|\s+$/g, ''));
    }, "¡Upss! deben ser ser solo letras");
    
    $.validator.addMethod("lettersnumberonly0", function(value, element) {
            var document = $("select[name='document_type']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("lettersnumberonly1", function(value, element) {
            var document = $("select[name='bfdocument1']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("lettersnumberonly2", function(value, element) {
            var document = $("select[name='bfdocument2']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("lettersnumberonly3", function(value, element) {
            var document = $("select[name='bfdocument3']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("lettersnumberonly4", function(value, element) {
            var document = $("select[name='bfdocument4']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("lettersnumberonly5", function(value, element) {
            var document = $("select[name='bfdocument5']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("lettersnumberonly6", function(value, element) {
            var document = $("select[name='bfdocument6']").val();
            if (document == '7' || document == '8') { //pasaporte y documento de identificación extrangera
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
    $.validator.addMethod("documentrange", function(value, element) {
            var document = $("select[name='numero_documento']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
        }, "¡Upss! cantidad de digitos no es correcto");
    $.validator.addMethod("documentrange1", function(value, element) {
            var document = $("select[name='bfdocument1']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
    $.validator.addMethod("documentrange2", function(value, element) {
            var document = $("select[name='bfdocument2']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
    $.validator.addMethod("documentrange3", function(value, element) {
            var document = $("select[name='bfdocument3']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
    $.validator.addMethod("documentrange4", function(value, element) {
            var document = $("select[name='bfdocument4']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
    $.validator.addMethod("documentrange5", function(value, element) {
            var document = $("select[name='bfdocument5']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
    $.validator.addMethod("documentrange6", function(value, element) {
            var document = $("select[name='bfdocument6']").val();
            if (document == '3') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
    
    $.validator.addMethod("uniquedocument1", function(value, element) {
            var numero_documento = $("input[name='numero_documento']").val();
            var document_type = $("select[name='document_type']").val();
            var bfdocument1 = $("select[name='bfdocument1']").val();
            
            var bfnumero_documento2 = $("input[name='bfnumero_documento2']").val();
            var bfdocument2 = $("select[name='bfdocument2']").val();
            var bfnumero_documento3 = $("input[name='bfnumero_documento3']").val();
            var bfdocument3 = $("select[name='bfdocument3']").val();
            var bfnumero_documento4 = $("input[name='bfnumero_documento4']").val();
            var bfdocument4 = $("select[name='bfdocument4']").val();
            var bfnumero_documento5 = $("input[name='bfnumero_documento5']").val();
            var bfdocument5 = $("select[name='bfdocument5']").val();
            var bfnumero_documento6 = $("input[name='bfnumero_documento6']").val();
            var bfdocument6 = $("select[name='bfdocument6']").val();
            if (value == numero_documento && document_type == bfdocument1) {
                return false;
            }
            if (value == bfnumero_documento2 && bfdocument1 == bfdocument2) {
                return false;
            }
            if (value == bfnumero_documento3 && bfdocument1 == bfdocument3) {
                return false;
            }
            if (value == bfnumero_documento4 && bfdocument1 == bfdocument4) {
                return false;
            }
            if (value == bfnumero_documento5 && bfdocument1 == bfdocument5) {
                return false;
            }
            if (value == bfnumero_documento6 && bfdocument1 == bfdocument6) {
                return false;
            }
            return true;
        }, "¡Upss! número de documento repetido");
    
    $.validator.addMethod("uniquedocument2", function(value, element) {
            var numero_documento = $("input[name='numero_documento']").val();
            var document_type = $("select[name='document_type']").val();
            var bfdocument2 = $("select[name='bfdocument2']").val();
        
            var bfnumero_documento1 = $("input[name='bfnumero_documento1']").val();
            var bfdocument1 = $("select[name='bfdocument1']").val();
            var bfnumero_documento3 = $("input[name='bfnumero_documento3']").val();
            var bfdocument3 = $("select[name='bfdocument3']").val();
            var bfnumero_documento4 = $("input[name='bfnumero_documento4']").val();
            var bfdocument4 = $("select[name='bfdocument4']").val();
            var bfnumero_documento5 = $("input[name='bfnumero_documento5']").val();
            var bfdocument5 = $("select[name='bfdocument5']").val();
            var bfnumero_documento6 = $("input[name='bfnumero_documento6']").val();
            var bfdocument6 = $("select[name='bfdocument6']").val();
            if (value == numero_documento && document_type == bfdocument2) {
                return false;
            }
            if (value == bfnumero_documento1 && bfdocument2 == bfdocument1) {
                return false;
            }
            if (value == bfnumero_documento3 && bfdocument2 == bfdocument3) {
                return false;
            }
            if (value == bfnumero_documento4 && bfdocument2 == bfdocument4) {
                return false;
            }
            if (value == bfnumero_documento5 && bfdocument2 == bfdocument5) {
                return false;
            }
            if (value == bfnumero_documento6 && bfdocument2 == bfdocument6) {
                return false;
            }
            return true;
        }, "¡Upss! número de documento repetido");
    
    $.validator.addMethod("uniquedocument3", function(value, element) {
            var numero_documento = $("input[name='numero_documento']").val();
            var document_type = $("select[name='document_type']").val();
            var bfdocument3 = $("select[name='bfdocument3']").val();
        
            var bfnumero_documento1 = $("input[name='bfnumero_documento1']").val();
            var bfdocument1 = $("select[name='bfdocument1']").val();
            var bfnumero_documento2 = $("input[name='bfnumero_documento2']").val();
            var bfdocument2 = $("select[name='bfdocument2']").val();
            var bfnumero_documento4 = $("input[name='bfnumero_documento4']").val();
            var bfdocument4 = $("select[name='bfdocument4']").val();
            var bfnumero_documento5 = $("input[name='bfnumero_documento5']").val();
            var bfdocument5 = $("select[name='bfdocument5']").val();
            var bfnumero_documento6 = $("input[name='bfnumero_documento6']").val();
            var bfdocument6 = $("select[name='bfdocument6']").val();
            if (value == numero_documento && document_type == bfdocument3) { //cédula de ciudadanía
                return false;
            }
            if (value == bfnumero_documento1 && bfdocument3 == bfdocument1) {
                return false;
            }
            if (value == bfnumero_documento2 && bfdocument3 == bfdocument2) {
                return false;
            }
            if (value == bfnumero_documento4 && bfdocument3 == bfdocument4) {
                return false;
            }
            if (value == bfnumero_documento5 && bfdocument3 == bfdocument5) {
                return false;
            }
            if (value == bfnumero_documento6 && bfdocument3 == bfdocument6) {
                return false;
            }
            return true;
        }, "¡Upss! número de documento repetido");
    
    $.validator.addMethod("uniquedocument4", function(value, element) {
            var numero_documento = $("input[name='numero_documento']").val();
            var document_type = $("select[name='document_type']").val();
            var bfdocument4 = $("select[name='bfdocument4']").val();
        
            var bfnumero_documento1 = $("input[name='bfnumero_documento1']").val();
            var bfdocument1 = $("select[name='bfdocument1']").val();
            var bfnumero_documento2 = $("input[name='bfnumero_documento2']").val();
            var bfdocument2 = $("select[name='bfdocument2']").val();
            var bfnumero_documento3 = $("input[name='bfnumero_documento3']").val();
            var bfdocument3 = $("select[name='bfdocument3']").val();
            var bfnumero_documento5 = $("input[name='bfnumero_documento5']").val();
            var bfdocument5 = $("select[name='bfdocument5']").val();
            var bfnumero_documento6 = $("input[name='bfnumero_documento6']").val();
            var bfdocument6 = $("select[name='bfdocument6']").val();
            if (value == numero_documento && document_type == bfdocument4) { //cédula de ciudadanía
                return false;
            }
            if (value == bfnumero_documento1 && bfdocument4 == bfdocument1) {
                return false;
            }
            if (value == bfnumero_documento2 && bfdocument4 == bfdocument2) {
                return false;
            }
            if (value == bfnumero_documento3 && bfdocument4 == bfdocument3) {
                return false;
            }
            if (value == bfnumero_documento5 && bfdocument4 == bfdocument5) {
                return false;
            }
            if (value == bfnumero_documento6 && bfdocument4 == bfdocument6) {
                return false;
            }
            return true;
        }, "¡Upss! número de documento repetido");
    
    $.validator.addMethod("uniquedocument5", function(value, element) {
            var numero_documento = $("input[name='numero_documento']").val();
            var document_type = $("select[name='document_type']").val();
            var bfdocument5 = $("select[name='bfdocument5']").val();
        
            var bfnumero_documento1 = $("input[name='bfnumero_documento1']").val();
            var bfdocument1 = $("select[name='bfdocument1']").val();
            var bfnumero_documento2 = $("input[name='bfnumero_documento2']").val();
            var bfdocument2 = $("select[name='bfdocument2']").val();
            var bfnumero_documento3 = $("input[name='bfnumero_documento3']").val();
            var bfdocument3 = $("select[name='bfdocument3']").val();
            var bfnumero_documento4 = $("input[name='bfnumero_documento4']").val();
            var bfdocument4 = $("select[name='bfdocument4']").val();
            var bfnumero_documento6 = $("input[name='bfnumero_documento6']").val();
            var bfdocument6 = $("select[name='bfdocument6']").val();
            if (value == numero_documento && document_type == bfdocument5) { //cédula de ciudadanía
                return false;
            }
            if (value == bfnumero_documento1 && bfdocument5 == bfdocument1) {
                return false;
            }
            if (value == bfnumero_documento2 && bfdocument5 == bfdocument2) {
                return false;
            }
            if (value == bfnumero_documento3 && bfdocument5 == bfdocument3) {
                return false;
            }
            if (value == bfnumero_documento4 && bfdocument5 == bfdocument4) {
                return false;
            }
            if (value == bfnumero_documento6 && bfdocument5 == bfdocument6) {
                return false;
            }
            return true;
        }, "¡Upss! número de documento repetido");
    
    $.validator.addMethod("uniquedocument6", function(value, element) {
            var numero_documento = $("input[name='numero_documento']").val();
            var document_type = $("select[name='document_type']").val();
            var bfdocument6 = $("select[name='bfdocument6']").val();
            var bfnumero_documento1 = $("input[name='bfnumero_documento1']").val();
            var bfdocument1 = $("select[name='bfdocument1']").val();
            var bfnumero_documento2 = $("input[name='bfnumero_documento2']").val();
            var bfdocument2 = $("select[name='bfdocument2']").val();
            var bfnumero_documento3 = $("input[name='bfnumero_documento3']").val();
            var bfdocument3 = $("select[name='bfdocument3']").val();
            var bfnumero_documento4 = $("input[name='bfnumero_documento4']").val();
            var bfdocument4 = $("select[name='bfdocument4']").val();
            var bfnumero_documento5 = $("input[name='bfnumero_documento5']").val();
            var bfdocument5 = $("select[name='bfdocument5']").val();
            if (value == numero_documento && document_type == bfdocument6) { //cédula de ciudadanía
                return false;
            }
            if (value == bfnumero_documento1 && bfdocument6 == bfdocument1) {
                return false;
            }
            if (value == bfnumero_documento2 && bfdocument6 == bfdocument2) {
                return false;
            }
            if (value == bfnumero_documento3 && bfdocument6 == bfdocument3) {
                return false;
            }
            if (value == bfnumero_documento4 && bfdocument6 == bfdocument4) {
                return false;
            }
            if (value == bfnumero_documento5 && bfdocument6 == bfdocument5) {
                return false;
            }
            return true;
        }, "¡Upss! número de documento repetido");
    
        $.validator.addMethod("email2", function(value, element) {
            return this.optional(element) || /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i.test(value);
        }, "¡Upss! deben contener caracteres validos");
    

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
                    email2: true,
                    email: true
                },
                phone: {
                    required: true,
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
                    lettersnumberonly0: true,
                    documentrange: true,
                },
                address: {
                    required: true,
                    minlength: 3,
                    maxlength: 100,
                },
                city: {
                    required: true,
                },
                country_address_id: {
                    required: true,
                },
                deparment: {
                    required: true,
                },
                state_address_id: {
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
                expedition_date: {
                    required: true,
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='expedition_date']").val();
                            let expedition_date = new Date(fecha);
                            let hoy = new Date();
                            if (expedition_date > hoy) {
                                return true;
                            }
  
                        }
                    },
                    min: {
                        depends: function(elem) {
                            let birthdate_date_form = $("input[name='date']").val();
                            let expedition_date_form = $("input[name='expedition_date']").val();
                            let birthdate_date = new Date(birthdate_date_form);
                            let expedition_date = new Date(expedition_date_form);
                            let hoy = new Date();
                            if (expedition_date <= birthdate_date) {
                                return true;
                            }
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
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname12: {
                    minlength: 3,
                    lettersonly: true,
                },
                bfemail1: {
                    required: true,
                    email2: true,
                    email: true
                },
                bfphone1: {
                    required: true,
                    formMovilFijoLength: true,
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
                    lettersnumberonly1: true,
                    documentrange1: true,
                    uniquedocument1: true,
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate1']").val();
                            let birthdate_date = new Date(fecha);
                            let hoy = new Date();
                            if (birthdate_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate1']").val();
                            let fecha_principal = $("input[name='date']").val();
                            let parentesco = $("select[name='bfparentesco1']").val();
                            let birthdate_beneficiary = new Date(fecha);
                            let birthdate_main = new Date(fecha_principal);
                            let hoy = new Date();
                            if (birthdate_beneficiary <= birthdate_main && parentesco == 'H') {
                                return true;
                            }
                        }
                    },
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
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname22: {
                    minlength: 3,
                    lettersonly: true,
                },
                bfemail2: {
                    required: true,
                    email2: true,
                    email: true
                },
                bfphone2: {
                    required: true,
                    formMovilFijoLength: true,
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
                    lettersnumberonly2: true,
                    documentrange2: true,
                    uniquedocument2: true,
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate2']").val();
                            let birthdate_date = new Date(fecha);
                            let hoy = new Date();
                            if (birthdate_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate2']").val();
                            let fecha_principal = $("input[name='date']").val();
                            let parentesco = $("select[name='bfparentesco2']").val();
                            let birthdate_beneficiary = new Date(fecha);
                            let birthdate_main = new Date(fecha_principal);
                            let hoy = new Date();
                            if (birthdate_beneficiary <= birthdate_main && parentesco == 'H') {
                                return true;
                            }
                        }
                    },
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
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname32: {
                    minlength: 3,
                    lettersonly: true,
                },
                bfemail3: {
                    required: true,
                    email2: true,
                    email: true
                },
                bfphone3: {
                    required: true,
                    formMovilFijoLength: true,
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
                    lettersnumberonly3: true,
                    documentrange3: true,
                    uniquedocument3: true,
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate3']").val();
                            let birthdate_date = new Date(fecha);
                            let hoy = new Date();
                            if (birthdate_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate3']").val();
                            let fecha_principal = $("input[name='date']").val();
                            let parentesco = $("select[name='bfparentesco3']").val();
                            let birthdate_beneficiary = new Date(fecha);
                            let birthdate_main = new Date(fecha_principal);
                            let hoy = new Date();
                            if (birthdate_beneficiary <= birthdate_main && parentesco == 'H') {
                                return true;
                            }
                        }
                    },
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
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname42: {
                    minlength: 3,
                    lettersonly: true,
                },
                bfemail4: {
                    required: true,
                    email2: true,
                    email: true
                },
                bfphone4: {
                    required: true,
                    formMovilFijoLength: true,
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
                    lettersnumberonly4: true,
                    documentrange4: true,
                    uniquedocument4: true,
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate4']").val();
                            let birthdate_date = new Date(fecha);
                            let hoy = new Date();
                            if (birthdate_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate4']").val();
                            let fecha_principal = $("input[name='date']").val();
                            let parentesco = $("select[name='bfparentesco4']").val();
                            let birthdate_beneficiary = new Date(fecha);
                            let birthdate_main = new Date(fecha_principal);
                            let hoy = new Date();
                            if (birthdate_beneficiary <= birthdate_main && parentesco == 'H') {
                                return true;
                            }
                        }
                    },
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
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname52: {
                    minlength: 3,
                    lettersonly: true,
                },
                bfemail5: {
                    required: true,
                    email2: true,
                    email: true
                },
                bfphone5: {
                    required: true,
                    formMovilFijoLength: true,
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
                    lettersnumberonly5: true,
                    documentrange5: true,
                    uniquedocument5: true,
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate5']").val();
                            let birthdate_date = new Date(fecha);
                            let hoy = new Date();
                            if (birthdate_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate5']").val();
                            let fecha_principal = $("input[name='date']").val();
                            let parentesco = $("select[name='bfparentesco5']").val();
                            let birthdate_beneficiary = new Date(fecha);
                            let birthdate_main = new Date(fecha_principal);
                            let hoy = new Date();
                            if (birthdate_beneficiary <= birthdate_main && parentesco == 'H') {
                                return true;
                            }
                        }
                    },
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
                    minlength: 3,
                    lettersonly: true,
                },
                bflastname62: {
                    minlength: 3,
                    lettersonly: true,
                },
                bfemail6: {
                    required: true,
                    email2: true,
                    email: true
                },
                bfphone6: {
                    required: true,
                    formMovilFijoLength: true,
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
                    lettersnumberonly6: true,
                    documentrange6: true,
                    uniquedocument6: true,
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
                    max: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate6']").val();
                            let birthdate_date = new Date(fecha);
                            let hoy = new Date();
                            if (birthdate_date > hoy) {
                                return true;
                            }
                        }
                    },
                    min: {
                        depends: function(elem) { 
                            let fecha = $("input[name='bfdate6']").val();
                            let fecha_principal = $("input[name='date']").val();
                            let parentesco = $("select[name='bfparentesco6']").val();
                            let birthdate_beneficiary = new Date(fecha);
                            let birthdate_main = new Date(fecha_principal);
                            let hoy = new Date();
                            if (birthdate_beneficiary <= birthdate_main && parentesco == 'H') {
                                return true;
                            }
                        }
                    },
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
                    email2: "¡Upss! escribe un email valido",
                    email: "¡Upss! escribe un email valido"
                },
                phone: {
                    required: "¡Upss! un telefono es requerido",                    
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
                    lettersnumberonly0: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument: "¡Upss! número de documento repetido",
                },
                address: {
                    required: "¡Upss! una dirección es requerida",
                    minlength: "¡Upss! una dirección contiene más de 3 caracteres",
                    maxlength: "¡Upss! tu dirección no puede tener más de 100 caracteres",
                },
                city: {
                    required: "¡Upss! una ciudad es requerida",
                },
                country_address_id: {
                    required: "¡Upss! un país es requerido",
                },
                deparment: {
                    required: "¡Upss! un departamento es requerido",
                },
                state_address_id: {
                    required: "¡Upss! un departamento es requerido",
                },
                date: {
                    required: "¡Upss! una fecha de nacimiento es requerido",
                    min: "¡Upss! fecha invalida",
                    max: "¡Upss! debes de ser  menor de 69 años para continuar"
                },
                expedition_date: {
                    required: "¡Upss! tu fecha de expedición es requerido",
                    min: "¡Upss! debe ser superior a la fecha de nacimiento",
                    max: "¡Upss! debe ser igual o inferior a la fecha actual"
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
                    email2: "¡Upss! escribe un email valido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone1: {
                    required: "¡Upss! un telefono es requerido",
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
                    lettersnumberonly1: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange1: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument1: "¡Upss! número de documento repetido",
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
                    max: "¡Upss! debe ser una fecha inferior o igual a la fecha actual",
                    min: "¡Upss! tú hijo no puede ser mayor a ti"
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
                    email2: "¡Upss! escribe un email valido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone2: {
                    required: "¡Upss! un telefono es requerido",                    
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
                    lettersnumberonly2: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange2: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument2: "¡Upss! número de documento repetido",
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
                    max: "¡Upss! debe ser una fecha inferior o igual a la fecha actual",
                    min: "¡Upss! tú hijo no puede ser mayor a ti"
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
                    email2: "¡Upss! Escribe un email valido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone3: {
                    required: "¡Upss! tu telefono es requerido", 
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
                    lettersnumberonly3: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange3: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument3: "¡Upss! número de documento repetido",
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
                    max: "¡Upss! debe ser una fecha inferior o igual a la fecha actual",
                    min: "¡Upss! tú hijo no puede ser mayor a ti"
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
                    email2: "¡Upss! Escribe un email valido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone4: {
                    required: "¡Upss! tu telefono es requerido",
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
                    lettersnumberonly4: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange4: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument4: "¡Upss! número de documento repetido",
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
                    max: "¡Upss! debe ser una fecha inferior o igual a la fecha actual",
                    min: "¡Upss! tú hijo no puede ser mayor a ti"
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
                },
                bfphone5: {
                    required: "¡Upss! tu telefono es requerido", 
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
                    lettersnumberonly5: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange5: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument5: "¡Upss! número de documento repetido",
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
                    max: "¡Upss! debe ser una fecha inferior o igual a la fecha actual",
                    min: "¡Upss! tú hijo no puede ser mayor a ti"
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
                    email2: "Upss! Escribe un email valido",
                    email: "¡Upss! escribe un email valido"
                },
                bfphone6: {
                    required: "¡Upss! tu telefono es requerido",
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
                    lettersnumberonly6: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange6: "¡Upss! cantidad de digitos no es correcto",
                    uniquedocument6: "¡Upss! número de documento repetido",
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
                    max: "¡Upss! debe ser una fecha inferior o igual a la fecha actual",
                    min: "¡Upss! tú hijo no puede ser mayor a ti"
                },
            }
        });
    
    let estado_civil = $("select[name='estado_civil']").val();
    if (estado_civil == 'Soltero') {
        let newOptions = {
            Seleccione: "",
            Padres: "D",
            Hijos: "H",
            Hermanos: "M"
        };
        for (let index = 0; index < 6; index++) {
            let id_elemento = 'bfparentesco' + (index + 1);
            let elemento = "select[name='" + id_elemento + "']";
            let elemento_completo = $(elemento);
            elemento_completo.empty();
            $.each(newOptions, function(key, value) {
                elemento_completo.append($("<option></option>")
                    .attr("value", value).text(key));
            });
        }
    }
    if (estado_civil == 'Viudo') {
        let newOptions = {
            Seleccione: "",
            Padres: "D",
            Hijos: "H",
            Hermanos: "M",
            Suegros: "S"
        };
        for (let index = 0; index < 6; index++) {
            let id_elemento = 'bfparentesco' + (index + 1);
            let elemento = "select[name='" + id_elemento + "']";
            let elemento_completo = $(elemento);
            elemento_completo.empty();
            $.each(newOptions, function(key, value) {
                elemento_completo.append($("<option></option>")
                    .attr("value", value).text(key));
            });
        }
    }
    
    
    $("#submit_beneficiaries").on('click', function(e){
      /*
      var calendar_datetime = $(".appointment_portal_edit_form input[name='calendar_datetime']").val();
      if (calendar_datetime === '' || calendar_datetime === null || calendar_datetime === 'undefined'){
        Dialog.alert(this, 'Por favor selecione una fecha de realización!');
        return false;
      };
      $(".appointment_portal_edit_form").submit();
      */
      //a-submit a-submit-disable a-submit-loading
      //$("#submit_beneficiaries").hide();
      return true;
    });

});


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
        
        $('#submit_pse_end_add_beneficiaries').on('click', function() {
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
        
        $('#submit_credit_card_end').on('click', function() {
            var url = '/shop/payment'
            window.location.href = url;
        });
        
        $('#submit_pse_end').on('click', function() {
            var url = '/shop/payment'
            window.location.href = url;
        });
        
        $('#submit_payment_cash_success').on('click', function() {
            var url = '/shop'
            window.location.href = url;
        });
        
        function consultarEstadosCreditCard(pais) {
            $.ajax({
                data: { 'id': pais },
                url: "/search/states",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);                    
                    $('#credit_card_state_id').selectpicker('destroy');
                    $('#credit_card_state_id').empty();
                    $('#credit_card_city').selectpicker('destroy');
                    $('#credit_card_city').empty();
                    decode_data.data.states.forEach(function(obj) {
                        $('#credit_card_state_id').append($("<option></option>")
                            .attr("value", obj.state_id).text(obj.state));
                    });
                    let estado = $('#credit_card_state_id').val();
                    let elemento = "select[name='credit_card_city']";
                    consultarCiudadesCreditCard(estado, elemento);
                    $('#credit_card_state_id').selectpicker('render');
                    $('#credit_card_city').selectpicker('render');
                    
                }
            });
        }
        
        
        
        function consultarEstadosCash(pais) {
            $.ajax({
                data: { 'id': pais },
                url: "/search/states",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);                    
                    $('#cash_state_id').selectpicker('destroy');
                    $('#cash_state_id').empty();
                    $('#cash_city').selectpicker('destroy');
                    $('#cash_city').empty();
                    decode_data.data.states.forEach(function(obj) {
                        $('#cash_state_id').append($("<option></option>")
                            .attr("value", obj.state_id).text(obj.state));
                    });
                    let estado = $('#cash_state_id').val();
                    let elemento = "select[name='cash_city']";
                    consultarCiudadesCash(estado, elemento);
                    $('#cash_state_id').selectpicker('render');
                    $('#cash_city').selectpicker('render');
                    
                }
            });
        }
        
        
        
        function consultarEstadosPse(pais) {
            $.ajax({
                data: { 'id': pais },
                url: "/search/states",
                type: 'get',
                success: function(data) {
                    let decode_data = JSON.parse(data);                    
                    $('#pse_state_id').selectpicker('destroy');
                    $('#pse_state_id').empty();
                    $('#pse_city').selectpicker('destroy');
                    $('#pse_city').empty();
                    decode_data.data.states.forEach(function(obj) {
                        $('#pse_state_id').append($("<option></option>")
                            .attr("value", obj.state_id).text(obj.state));
                    });
                    let estado = $('#pse_state_id').val();
                    let elemento = "select[name='pse_city']";
                    consultarCiudadesPSE(estado, elemento);
                    $('#pse_state_id').selectpicker('render');
                    $('#pse_city').selectpicker('render');
                    
                }
            });
        }
        
        
        $('#credit_card_country_id').change(function() {
            let data_select = $("#credit_card_country_id option:selected").val();            
            if (data_select != 49){               
                $('.div_state').hide();
                $('.div_city').hide();
                $('.div_state_text').show();
                $('.div_city_text').show();
            }
            else{ 
                consultarEstadosCreditCard(data_select);                
                $('.div_state_text').hide();
                $('.div_city_text').hide();
                $('.div_state').show();
                $('.div_city').show();   
            }
        });
        
        
        $('#pse_country_id').change(function() {
            let data_select = $("#pse_country_id option:selected").val();            
            if (data_select != 49){               
                $('.div_state').hide();
                $('.div_city').hide();
                $('.div_state_text').show();
                $('.div_city_text').show();
            }
            else{ 
                consultarEstadosCreditCard(data_select);                
                $('.div_state_text').hide();
                $('.div_city_text').hide();
                $('.div_state').show();
                $('.div_city').show();   
            }
        });
        
        $('#cash_country_id').change(function() {
            let data_select = $("#cash_country_id option:selected").val();            
            if (data_select != 49){               
                $('.div_state').hide();
                $('.div_city').hide();
                $('.div_state_text').show();
                $('.div_city_text').show();
            }
            else{ 
                consultarEstadosCreditCard(data_select);                
                $('.div_state_text').hide();
                $('.div_city_text').hide();
                $('.div_state').show();
                $('.div_city').show();   
            }
        });
        
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
                    $("select[name='credit_card_city']").val($("input[name='partner_city_id']").val());
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
                    $("select[name='pse_city']").val($("input[name='partner_city_id']").val());
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
                    $("select[name='cash_city']").val($("input[name='partner_city_id']").val());
                    $('#cash_city').selectpicker();
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
        $("select[name='credit_card_city']").val(partner_city_id);
        $("select[name='pse_country_id']").val(partner_country_id);
        $("select[name='pse_state_id']").val(partner_state_id);
        $("select[name='pse_city']").val(partner_city_id);
        $("select[name='cash_country_id']").val(partner_country_id);
        $("select[name='cash_state_id']").val(partner_state_id);
        $("select[name='cash_city']").val(partner_city_id);
        $('#credit_card_country_id').selectpicker('refresh')
        $('#credit_card_state_id').selectpicker('refresh')
        $('#credit_card_city').selectpicker('refresh')
        $('#pse_country_id').selectpicker('refresh')
        $('#pse_state_id').selectpicker('refresh')
        $('#pse_city').selectpicker('refresh')
        $('#cash_country_id').selectpicker('refresh')
        $('#cash_state_id').selectpicker('refresh')
        $('#cash_city').selectpicker('refresh')
        
        
        if ($('#partner_document_type').val() == '3') {
            $("select[name='credit_card_partner_type']").val('CC');
            $("select[name='cash_partner_type']").val('CC');
            $("select[name='pse_partner_type']").val('CC');
        } else if ($('#partner_document_type').val() == '7') {
            $("select[name='credit_card_partner_type']").val('PP');
            $("select[name='cash_partner_type']").val('PP');
            $("select[name='pse_partner_type']").val('PP');
        } else if ($('#partner_document_type').val() == '5') {
            $("select[name='credit_card_partner_type']").val('CE');
            $("select[name='cash_partner_type']").val('CE');
            $("select[name='pse_partner_type']").val('CE');
        } else if ($('#partner_document_type').val() == '8') {
            $("select[name='credit_card_partner_type']").val('DE');
            $("select[name='cash_partner_type']").val('DE');
            $("select[name='pse_partner_type']").val('DE');
        }
        
        var credit_city = "select[name='credit_card_city']";
        var pse_city = "select[name='pse_city']";
        var cash_city = "select[name='cash_city']";
        if (partner_state_id){
            consultarCiudadesCreditCard(partner_state_id, credit_city);
            consultarCiudadesPSE(partner_state_id, pse_city);
            consultarCiudadesCash(partner_state_id, cash_city);
        }
       
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
        
        $.validator.addMethod("lettersnumberonly_creditcard", function(value, element) {
            var document = $("select[name='credit_card_partner_type']").val();
            if (document == 'PP') { //pasaporte
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
        $.validator.addMethod("lettersnumberonly_cash", function(value, element) {
            var document = $("select[name='cash_partner_type']").val();
            if (document == 'PP') { //pasaporte
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
        $.validator.addMethod("lettersnumberonly_pse", function(value, element) {
            var document = $("select[name='pse_partner_type']").val();
            if (document == 'PP') { //pasaporte
                return this.optional(element) || /^[A-Za-z0-9]*$/g.test(value);
            } else {
                return this.optional(element) || /^[0-9]*$/.test(value);
            }
        }, "¡Upss! deben ser ser solo letras");
        $.validator.addMethod("documentrange_credit_card", function(value, element) {
            var document = $("select[name='credit_card_partner_document']").val();
            if (document == 'CC') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
        $.validator.addMethod("documentrange_cash", function(value, element) {
            var document = $("select[name='cash_partner_document']").val();
            if (document == 'CC') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
        $.validator.addMethod("documentrange_pse", function(value, element) {
            var document = $("select[name='pse_partner_document']").val();
            if (document == 'CC') { //cédula de ciudadanía
                if ($.isNumeric(value) && (value < 99999 || value > 9999999999)) {
                    return false;
                } else {
                    return true;
                }
            }
            return true;
        }, "¡Upss! cantidad de digitos no es correcto");
        
        $.validator.addMethod("email2", function(value, element) {
            return this.optional(element) || /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i.test(value);
        }, "¡Upss! deben contener caracteres validos");


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
                    maxlength: 4,
                    number: true,
                },
                credit_card_name: {
                    required: true,
                    minlength: 3,
                    maxlength: 30,
                    //lettersonly: true,
                },
                credit_card_billing_firstname: {
                    required: true,
                    //lettersonly: true,
                },
                credit_card_billing_lastname: {
                    required: true,
                    //lettersonly: true,
                },
                credit_card_billing_email: {
                    required: true,
                    email2: true,
                },
                credit_card_partner_phone: {
                    required: true,                    
                    formMovilFijoLength: true,
                },
                credit_card_partner_document: {
                    required: true,
                    lettersnumberonly_creditcard: true,
                    documentrange_credit_card: true,
                },
                identification_document: {
                    required: true,
                },
                credit_card_partner_street: {
                    required: true,
                    minlength: 3,
                    maxlength: 100,
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
                    minlength: "¡Upss! debe contener entre 13 y 16 digitos",
                    maxlength: "¡Upss! debe contener entre 13 y 16 digitos"
                },
                credit_card_code: {
                    required: "¡Upss! el código de seguridad es requerido",
                    maxlength: "¡Upss! máximo 4 digitos"
                },
                credit_card_name: {
                    required: "¡Upss! el nombre de tajeta es requerido",
                    minlength: "¡Upss! debe contener 3 o más caracteres",
                    maxlength: "¡Upss! debe contener máximo 30 caracteres",
                    //lettersonly: "¡Upss! debe contener solo letras"
                },
                credit_card_partner_phone: {
                    required: "¡Upss! tu telefono es requerido",
                    minlength: "¡Upss! debe tener 10 digitos",
                    maxlength: "¡Upss! debe tener 10 digitos"

                },
                credit_card_billing_email: {
                    email2: "¡Upss! debe registrar un correo valido",
                },
                credit_card_billing_firstname: {
                    required: "¡Upss! tu(s) nombre(s) es requerido",
                },
                credit_card_billing_lastname: {
                    required: "¡Upss! tu(s) apellido(s) es requerido",
                },
                credit_card_partner_document: {
                    required: "¡Upss! tu numero de documento es requerido",
                    lettersnumberonly_creditcard: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange_caredit_card: "¡Upss! cantidad de digitos no es correcto",
                },
                identification_document: {
                    required: "¡Upss! tu numero de documento es requerido",
                },
                credit_card_partner_street: {
                    required: "¡Upss! tu dirección es requerida",
                    minlength: "¡Upss! una dirección contiene más de 3 caracteres",
                    maxlength: "¡Upss! tu dirección no puede tener más de 100 caracteres",
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
                cash_bank: {
                    required: true,
                },
                cash_billing_firstname: {
                    required: true,
                    lettersonly: true,
                },
                cash_billing_lastname: {
                    required: true,
                    lettersonly: true,
                },
                cash_partner_document: {
                    required: true,
                    lettersnumberonly_cash: true,
                    documentrange_cash: true,
                },
                cash_billing_email: {
                    required: true,
                    email2: true,
                },
                cash_partner_street: {
                    required: true,
                    minlength: 3,
                    maxlength: 100,
                },
                cash_country_id: {
                    required: true,
                },
                cash_state_id: {
                    required: true,
                },
                cash_city: {
                    required: true,
                },
            },
            messages: {
                cash_bank: {
                    required: "¡Upss! debe seleccionar un medio de pago Efectivo"
                },
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
                    lettersnumberonly_cash: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange_cash: "¡Upss! cantidad de digitos no es correcto",
                },
                cash_billing_email: {
                    required: "¡Upss! tu email es requerido",
                    email2: "¡Upss! debe contener un correo valido"
                },
                cash_partner_street: {
                    required: "¡Upss! tu documento es requerido",
                    minlength: "¡Upss! una dirección contiene más de 3 caracteres",
                    maxlength: "¡Upss! tu dirección no puede tener más de 100 caracteres",
                },
                cash_country_id: {
                    required: "¡Upss! debes seleccionar un país",
                },
                cash_state_id: {
                    required: "¡Upss! debes seleccionar un departamento",
                },
                cash_city: {
                    required: "¡Upss! debes seleccionar una ciudad",
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
                    lettersnumberonly_pse: true,
                    documentrange_pse: true,
                },
                pse_billing_email: {
                    required: true,
                    email2: true,
                },
                pse_partner_street: {
                    required: true,
                    minlength: 3,
                    maxlength: 100,
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
                    lettersnumberonly_pse: "¡Upss! solo números (y letras para pasaporte)",
                    documentrange_pse: "¡Upss! cantidad de digitos no es correcto",
                },
                pse_billing_email: {
                    required: "¡Upss! tu email es requerido",
                    email2: "¡Upss! debe contener un correo valido"
                },
                pse_partner_street: {
                    required: "¡Upss! tu documento es requerido",
                    minlength: "¡Upss! una dirección contiene más de 3 caracteres",
                    maxlength: "¡Upss! tu dirección no puede tener más de 100 caracteres",
                },
            }
        });
        
        var bank_url = $("#bank_url").val();
        var url_payment_receipt_pdf = $("#url_payment_receipt_pdf").val();
        var url_payment_receipt_html = $("#url_payment_receipt_html").val();
        if (bank_url) {
            window.open(bank_url);
        }
        if (url_payment_receipt_html) {
            window.open(url_payment_receipt_html);
        }
        if (url_payment_receipt_pdf) {
            window.open(url_payment_receipt_pdf);
        }
    });
   
});

 