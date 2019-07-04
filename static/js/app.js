$(document).ready(async function() {

  const $likeBtn = $("#like")
  const $unlikeBtn = $("#unlike")

  async function checkLike(){
    // returns True if current user likes cafe, else False
    let response = await axios.get("/api/likes", {
      params: {"cafe_id": cafe_id}
    });
    return response.data.likes;
  }

  async function displayProperButtons(){
    hideBtn($likeBtn);
    hideBtn($unlikeBtn);
    await checkLike() ? showBtn($unlikeBtn) : showBtn($likeBtn);
    return;
  }

  function hideBtn($btn){
    $btn.addClass("d-none");
  }

  function showBtn($btn){
    $btn.removeClass("d-none");
  }

  $likeBtn.on("click", async function(evt){
    evt.preventDefault();

    response = await axios.post("/api/like", {
      "cafe_id": cafe_id
    });
    hideBtn($likeBtn);
    showBtn($unlikeBtn);
  });

  $unlikeBtn.on("click", async function(evt){
    evt.preventDefault();

    response = await axios.post("/api/unlike", {
      "cafe_id": cafe_id
    })
    hideBtn($unlikeBtn);
    showBtn($likeBtn);
    });

  displayProperButtons()
})