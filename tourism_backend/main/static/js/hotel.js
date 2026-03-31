(function () {
  var hotelDescriptions = {
    ngorongoro: '<h2 class="hotel-modal-title">&Beyond Ngorongoro Crater Lodge</h2><p class="hotel-modal-copy">On the rim of the Ngorongoro Crater. Spectacular luxury safari experience with breathtaking views, Maasai-inspired design, baroque elegance, crystal chandeliers, vintage decor, gourmet cuisine, and exclusive access to the crater floor teeming with wildlife.</p>',
    fourseasons: '<h2 class="hotel-modal-title">Four Seasons Safari Lodge Serengeti</h2><p class="hotel-modal-copy">Central Serengeti. Five-star experience with spacious rooms, infinity pool overlooking a waterhole, world-class spa, game drives, and exquisite dining under the African stars. Witness the Great Migration in supreme comfort.</p>',
    serena: '<h2 class="hotel-modal-title">Serengeti Serena Safari Lodge</h2><p class="hotel-modal-copy">Serengeti National Park. Inspired by a traditional African village, stone-built dome-roofed buildings along a rocky ridge, stunning central pool, panoramic views of the savannah, and prime game-viewing location.</p>',
    treetops: '<h2 class="hotel-modal-title">Tarangire Treetops</h2><p class="hotel-modal-copy">Tarangire Conservation Area. Elevated rooms on stilts around baobab and marula trees, magical views, famous for large elephant herds, eco-luxury, adventure, tree-top restaurant, and viewing deck over a waterhole.</p>',
    greystoke: '<h2 class="hotel-modal-title">Greystoke Mahale</h2><p class="hotel-modal-copy">Lake Tanganyika, Mahale Mountains. Remote lodge on a white-sand beach, main activity is trekking to observe chimpanzees, rustic romance, built from reclaimed dhow boats, once-in-a-lifetime experience.</p>',
    hyatt: '<h2 class="hotel-modal-title">Park Hyatt Zanzibar</h2><p class="hotel-modal-copy">Stone Town. Luxury in historic buildings, Omani architecture, contemporary elegance, seafront location, courtyard pool, spa, world-class dining, steps from House of Wonders and Old Fort.</p>',
    zhotel: '<h2 class="hotel-modal-title">The Z Hotel Nungwi</h2><p class="hotel-modal-copy">Nungwi, Northern Tip. Stylish adults-only boutique hotel, infinity pool merging with the ocean, minimalist rooms, prime location on Zanzibar\\'s best beach, near lighthouse and dhow boat yards.</p>',
    baraza: '<h2 class="hotel-modal-title">Baraza Resort & Spa</h2><p class="hotel-modal-copy">Bwejuu Beach, East Coast. All-villa resort, Sultan\\'s palace design, ornate arches, hand-carved furniture, private pools, all-inclusive, pristine beach, near Jozani Chwaka Bay National Park.</p>',
    mnemba: '<h2 class="hotel-modal-title">Mnemba Island Lodge</h2><p class="hotel-modal-copy">Mnemba Atoll, Private Island. Ten rustic-chic bandas on the beach, best snorkeling and diving, dolphins and turtles, next to Marine Conservation Area.</p>',
    emerson: '<h2 class="hotel-modal-title">Emerson Spice Hotel</h2><p class="hotel-modal-copy">Stone Town. Boutique hotel in a restored merchant\\'s house, bohemian charm, rooftop tearoom, fine-dining restaurant, themed rooms, central location for exploring the old city.</p>'
  };

  function filterHotels(type) {
    var tanzania = document.querySelectorAll(".hotel-card.tanzania");
    var zanzibar = document.querySelectorAll(".hotel-card.zanzibar");
    var i;

    if (type === "tanzania") {
      for (i = 0; i < tanzania.length; i += 1) {
        tanzania[i].classList.remove("hotel-card-hidden");
      }
      for (i = 0; i < zanzibar.length; i += 1) {
        zanzibar[i].classList.add("hotel-card-hidden");
      }
    } else {
      for (i = 0; i < tanzania.length; i += 1) {
        tanzania[i].classList.add("hotel-card-hidden");
      }
      for (i = 0; i < zanzibar.length; i += 1) {
        zanzibar[i].classList.remove("hotel-card-hidden");
      }
    }
  }

  function closeHotelModal() {
    var modal = document.getElementById("hotel-modal");
    if (modal) {
      modal.classList.remove("active");
    }
  }

  function showHotelModal(hotel) {
    var details = hotelDescriptions[hotel];
    var formHtml = "";
    var modalDetails = document.getElementById("hotel-modal-details");
    var modal = document.getElementById("hotel-modal");

    if (!details || !modalDetails || !modal) {
      return;
    }

    formHtml += '<form id="hotel-booking-form" class="hotel-booking-form">';
    formHtml += "<h4>Book This Hotel</h4>";
    formHtml += '<input type="date" name="arrival" required placeholder="Arrival Date">';
    formHtml += '<input type="text" name="fullname" required placeholder="Full Name">';
    formHtml += '<input type="email" name="email" required placeholder="Email">';
    formHtml += '<input type="tel" name="phone" required placeholder="Phone Number">';
    formHtml += '<input type="number" name="visitors" required min="1" placeholder="Number of Visitors">';
    formHtml += '<input type="number" name="rooms" required min="1" placeholder="Number of Rooms">';
    formHtml += '<button type="submit" class="hotel-booking-submit">Book Now</button>';
    formHtml += "</form>";

    modalDetails.innerHTML = details + formHtml;
    modal.classList.add("active");

    setTimeout(function () {
      var bookingForm = document.getElementById("hotel-booking-form");

      if (!bookingForm) {
        return;
      }

      bookingForm.onsubmit = function (event) {
        var msg = document.getElementById("hotel-success");
        var hotelName;

        event.preventDefault();
        hotelName = document.querySelector("#hotel-modal-details h2").innerText;

        if (msg) {
          msg.innerText =
            'You have successfully booked "' +
            hotelName +
            '" for ' +
            bookingForm.fullname.value +
            " (" +
            bookingForm.visitors.value +
            " visitors, " +
            bookingForm.rooms.value +
            " rooms, arrival: " +
            bookingForm.arrival.value +
            ").";
          msg.classList.add("active");
          setTimeout(function () {
            msg.classList.remove("active");
          }, 5000);
        }

        bookingForm.reset();
        closeHotelModal();
      };
    }, 100);
  }

  window.filterHotels = filterHotels;
  window.showHotelModal = showHotelModal;
  window.closeHotelModal = closeHotelModal;
}());
