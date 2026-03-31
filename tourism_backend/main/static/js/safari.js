(function () {
  var parkDetails = {
    serengeti: {
      title: "Serengeti National Park: The Great Migration & Predator Package",
      desc: "Luxury mobile tented camps positioned to follow the Great Migration. Expert-guided game drives at dawn and dusk to witness dramatic river crossings and prolific predator action (lions, cheetahs, leopards). Includes a hot-air balloon safari over the endless plains followed by a champagne breakfast.",
      offers: ["Luxury Mobile Tented Camps", "Expert-Guided Game Drives", "Hot-Air Balloon Safari", "Champagne Breakfast"]
    },
    ngorongoro: {
      title: "Ngorongoro Conservation Area: The Crater & Culture Experience",
      desc: "Full-day 4x4 descent into the Ngorongoro Crater for Big Five viewing. Stay at a luxury lodge on the crater rim with breathtaking views. Includes a guided visit to a Maasai boma for an authentic cultural experience.",
      offers: ["Crater Safari", "Luxury Crater Rim Lodge", "Maasai Boma Visit", "Big Five Viewing"]
    },
    kilimanjaro: {
      title: "Kilimanjaro National Park: The Peak Climber's Journey",
      desc: "Fully-supported and guided trek up Marangu or Machame route to summit Africa's highest peak, Uhuru Peak (5,895m). Includes pre-climb briefings, all park fees, expert guides and porters, mountain huts or tent accommodation, and all meals. Celebration dinner and certificate upon descent.",
      offers: ["Guided Trek", "Mountain Huts/Tents", "Expert Guides & Porters", "Celebration Dinner"]
    },
    tarangire: {
      title: "Tarangire National Park: The Elephant & Baobab Safari",
      desc: "Intensive game drives along the Tarangire River, famous for massive herds of elephants and ancient baobab trees. Includes a specialized photographic safari and a sundowner experience amidst the baobabs.",
      offers: ["Game Drives", "Photographic Safari", "Sundowner Experience", "Baobab Viewing"]
    },
    manyara: {
      title: "Lake Manyara National Park: The Canopy & Lakeside Adventure",
      desc: "Traditional game drives to spot tree-climbing lions and baboons, guided canoe safari on the lake for birdwatching (flamingos, pelicans), and a treetop walkway experience in the groundwater forest.",
      offers: ["Game Drives", "Canoe Safari", "Treetop Walkway", "Birdwatching"]
    },
    selous: {
      title: "Selous Game Reserve: The Remote Wilderness & River Safari",
      desc: "Boat safaris on the Rufiji River to see hippos, crocodiles, and waterbirds, walking safaris led by an armed guide, and classic 4x4 game drives in one of Africa's largest protected areas.",
      offers: ["Boat Safari", "Walking Safari", "Classic Game Drives", "Remote Bush Camps"]
    },
    ruaha: {
      title: "Ruaha National Park: The Wild & Untamed Predator Package",
      desc: "Exclusive, remote safari camps for an off-the-grid experience. Focus on large prides of lions, rare African wild dogs, and vast elephant herds. Includes guided walking safaris and fly-camping under the stars.",
      offers: ["Remote Safari Camps", "Wild Dog Tracking", "Fly-Camping", "Walking Safaris"]
    },
    katavi: {
      title: "Katavi National Park: The Authentic Bush Experience",
      desc: "Charter flights to the remote park, game drives to witness dry-season concentrations of hippos and crocodiles, and guided walks in the untouched miombo woodlands. Experience solitude and raw, untouched Africa.",
      offers: ["Charter Flights", "Game Drives", "Guided Walks", "Miombo Woodland Exploration"]
    },
    mikumi: {
      title: "Mikumi National Park: The Accessible Wildlife Weekend",
      desc: "Easy road transfer from Dar es Salaam for a 2-3 day safari. Relaxed game drives on the Mkata Floodplain, ideal for spotting elephants, giraffes, and lions. Family-friendly option.",
      offers: ["Road Transfer", "Game Drives", "Family-Friendly Safari", "Mkata Floodplain Viewing"]
    },
    kitulo: {
      title: "Kitulo National Park: The Botanical & Hiking Wonderland",
      desc: "Guided botanical walks through the \"Garden of God\" to witness wildflower displays (Nov-April), including orchids and aloes. Scenic hikes to surrounding peaks and a picnic amidst floral meadows. Birding and serenity of the high-altitude plateau.",
      offers: ["Botanical Walks", "Scenic Hikes", "Picnic in Meadows", "Birding"]
    }
  };

  function closeModal() {
    var modal = document.getElementById("park-modal");
    if (modal) {
      modal.classList.remove("active");
    }
  }

  function openModal(park) {
    var modal = document.getElementById("park-modal");
    var details = parkDetails[park];
    var detailsContainer = document.getElementById("modal-details");
    var html = "";

    if (!modal || !details || !detailsContainer) {
      return;
    }

    html += '<h2 class="safari-modal-title">' + details.title + "</h2>";
    html += '<p class="safari-modal-copy">' + details.desc + "</p>";
    html += '<h4 class="safari-modal-subtitle">What We Offer</h4>';
    html += '<ul class="safari-offers-list">';
    details.offers.forEach(function (item) {
      html += "<li>" + item + "</li>";
    });
    html += "</ul>";
    html += '<div class="safari-inclusions">';
    html += "<h4>Package Inclusions</h4>";
    html += "<ul>";
    html += "<li>All park entry, camping, and concession fees</li>";
    html += "<li>Accommodation in luxury lodges, tented camps, and mobile migration camps</li>";
    html += "<li>Professional English-speaking safari guide and driver</li>";
    html += "<li>Private 4x4 safari vehicle with pop-up roof</li>";
    html += "<li>All meals and drinking water as specified</li>";
    html += "<li>Domestic flights between remote parks</li>";
    html += "<li>All activities mentioned in each park's description</li>";
    html += "</ul>";
    html += '<p class="safari-inclusions-note">This package can be customized for photography, birding, hiking, or luxury.</p>';
    html += "</div>";
    html += '<form class="safari-booking-form">';
    html += "<h4>Book This Experience</h4>";
    html += "<input type=\"text\" placeholder=\"Your Name\" required>";
    html += "<input type=\"email\" placeholder=\"Your Email\" required>";
    html += "<input type=\"tel\" placeholder=\"Phone Number\" required>";
    html += '<button type="submit" class="safari-view-more-btn">Book Now</button>';
    html += "</form>";

    detailsContainer.innerHTML = html;
    modal.classList.add("active");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var modal = document.getElementById("park-modal");

    if (!modal) {
      return;
    }

    modal.addEventListener("click", function (event) {
      if (event.target === modal) {
        closeModal();
      }
    });
  });

  window.openModal = openModal;
  window.closeModal = closeModal;
}());
