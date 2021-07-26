// Store department choice to localStorage
$(document).ready(function () {
    AOS.init({ disable: 'mobile' });

    var activeTab = localStorage.getItem('dep');
    if (activeTab) {
        $('#item-1-1').removeClass('show active');
        $('#item-1-1-tab').removeClass('active');
        $('#' + activeTab).addClass('active');
        $('#' + activeTab.replace('-tab', '')).addClass('show active');
    }


    function autocomplete(inp, arr) {
        var currentFocus;
        inp.addEventListener("input", function (e) {
            var a, b, i, val = this.value;
            closeAllLists();
            if (!val) {
                $('#courseLink').val('');
                return false;
            }
            currentFocus = -1;
            a = document.createElement("DIV");
            a.setAttribute("id", this.id + "autocomplete-list");
            a.setAttribute("class", "autocomplete-items");
            this.parentNode.appendChild(a);
            for (i = 0; i < arr.length; i++) {
                if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                    b = document.createElement("DIV");
                    b.innerHTML = "<strong>" + arr[i].substr(0, val.length).toUpperCase() + "</strong>";
                    b.innerHTML += arr[i].substr(val.length).toUpperCase();
                    b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                    b.addEventListener("click", function (e) {
                        inp.value = this.getElementsByTagName("input")[0].value.toUpperCase();
                        $('#courseLink').val(inp.value + '.fcit18.link');
                        closeAllLists();
                    });
                    a.appendChild(b);
                }
            }
        });
        /*execute a function presses a key on the keyboard:*/
        inp.addEventListener("keydown", function (e) {
            var x = document.getElementById(this.id + "autocomplete-list");
            if (x) x = x.getElementsByTagName("div");
            if (e.keyCode == 40) {
                /*If the arrow DOWN key is pressed,
                increase the currentFocus variable:*/
                currentFocus++;
                /*and and make the current item more visible:*/
                addActive(x);
            } else if (e.keyCode == 38) { //up
                /*If the arrow UP key is pressed,
                decrease the currentFocus variable:*/
                currentFocus--;
                /*and and make the current item more visible:*/
                addActive(x);
            } else if (e.keyCode == 13) {
                /*If the ENTER key is pressed, prevent the form from being submitted,*/
                e.preventDefault();
                if (currentFocus > -1) {
                    /*and simulate a click on the "active" item:*/
                    if (x) x[currentFocus].click();
                }
            }
        });
        function addActive(x) {
            /*a function to classify an item as "active":*/
            if (!x) return false;
            /*start by removing the "active" class on all items:*/
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = (x.length - 1);
            /*add class "autocomplete-active":*/
            x[currentFocus].classList.add("autocomplete-active");
        }
        function removeActive(x) {
            /*a function to remove the "active" class from all autocomplete items:*/
            for (var i = 0; i < x.length; i++) {
                x[i].classList.remove("autocomplete-active");
            }
        }
        function closeAllLists(elmnt) {
            /*close all autocomplete lists in the document,
            except the one passed as an argument:*/
            var x = document.getElementsByClassName("autocomplete-items");
            for (var i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != inp) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }
        /*execute a function when someone clicks in the document:*/
        document.addEventListener("click", function (e) {
            closeAllLists(e.target);
        });
    }

    // TODO replace the array to be fetched from the api
    var courses = ["chem205", "cpis320", "arab201", "com205", "cpit250", "cpcs203", "cpcs212", "cpcs204", "cpcs202", "cpis250", "cpit210", "bus232", "cpis352", "cpcs301", "cpis420", "cpcs331", "bus233", "cpis240", "arab101", "cpis334", "cpis210", "bus230", "cpis354", "cpis380", "cpcs211", "cpcs214", "bio202", "cpis358", "cpis428", "cpit221", "cpcs223", "cpcs302", "cpis222", "cpcs351", "cpcs371", "cpcs241", "cpis312", "astr201", "cpcs324", "cpis342", "cpit201", "cpcs222", "cpcs361", "cpis351", "cpis370", "cpis220", "cpit220", "cpcs391", "soc210", "stat210", "cpcs381", "cpit285", "act333", "cpit323", "cpit240", "cpit260", "stat352", "cpit251", "cpit470", "cpit440", "math202", "isls201", "isls301", "cpit370", "plans", "isls401", "cpit280", "isls101", "cpit252", "cpit305", "cpit380", "cpit425", "is105", "cpit330", "cpit345"]
    autocomplete(document.getElementById("myInput"), courses);
});
function goCourse() {
    if ($('#courseLink').val() != "") {
        // redirect to 18 drive
        window.open("http://" + $('#courseLink').val(), '_blank').focus();
        // TODO add modal with list of all drives?
    }
}