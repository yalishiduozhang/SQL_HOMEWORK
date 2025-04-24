/**
 * 获取URL参数
 */
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

/**
 * 在指定容器中添加电影列表（根据类别）
 */
function addGenreRow(container, genre, collectionId, size, baseUrl) {
    $(container).append(
        '<div class="frontpage-section">' +
        '  <div class="frontpage-section-header">' +
        '    <div class="label collection-label">'+ genre +'</div>' +
        '  </div>' +
        '  <div id="' + collectionId + '" class="collection-panel">' +
        '  </div>' +
        '</div>'
    );

    $.getJSON(baseUrl + 'getrecommendation?genre=' + genre + '&size=' + size, function (data) {
        showMovies(data, '#' + collectionId);
    });
}

/**
 * 显示电影列表
 */
function showMovies(data, container) {
    if (data.length === 0) {
        return;
    }

    var moviePanel = $(container);
    moviePanel.empty();

    $.each(data, function (i, movie) {
        var movieId = movie.movieId;
        var title = movie.title;
        var rating = movie.averageRating;
        var releaseYear = movie.releaseYear;
        //var imgSrc = "https://image.tmdb.org/t/p/w500" + movie.tmdbId;
        var imgSrc = "/static/posters/" + movieId + ".jpg";
        var genres = "";
        if (movie.genres && movie.genres.length > 0) {
            genres = movie.genres.join(", ");
        }

        var movieDiv = $("<div>", {
            class: "movie-card",
            "data-movieid": movieId
        });

        var movieLink = $("<a>", {
            href: "movie.html?id=" + movieId + "&model=default",
            class: "movie-card-link"
        });

        var moviePoster = $("<div>", {
            class: "poster-wrapper"
        });

        var posterImg = $("<img>", {
            src: imgSrc,
            onerror: "this.onerror=null;this.src='static/images/default-poster.jpg';",
            class: "poster"
        });

        var movieInfo = $("<div>", {
            class: "movie-meta"
        });

        var movieTitle = $("<div>", {
            class: "title",
            text: title + (releaseYear ? " (" + releaseYear + ")" : "")
        });

        var movieRating = $("<div>", {
            class: "rating",
            text: rating === 0 ? "N/A" : rating.toFixed(1)
        });

        var movieGenres = $("<div>", {
            class: "genres",
            text: genres
        });

        // 组合元素
        moviePoster.append(posterImg);
        movieInfo.append(movieTitle, movieRating, movieGenres);
        movieLink.append(moviePoster, movieInfo);
        movieDiv.append(movieLink);
        moviePanel.append(movieDiv);
    });
}

/**
 * 显示电影详情
 */
function showMovieDetails(movie, container) {
    if (!movie || !movie.movieId) {
        return;
    }

    var moviePanel = $(container);
    moviePanel.empty();

    var title = movie.title;
    var rating = movie.averageRating;
    var releaseYear = movie.releaseYear;
    //var imgSrc = "https://image.tmdb.org/t/p/w500" + movie.tmdbId;
    var imgSrc = "/static/posters/" + movie.movieId + ".jpg";
    var genres = "";
    if (movie.genres && movie.genres.length > 0) {
        genres = movie.genres.join(", ");
    }

    var movieDetails = $("<div>", {
        class: "movie-details"
    });

    var posterCol = $("<div>", {
        class: "movie-poster-col"
    });

    var posterImg = $("<img>", {
        src: imgSrc,
        onerror: "this.onerror=null;this.src='static/images/default-poster.jpg';",
        class: "detail-poster"
    });

    var infoCol = $("<div>", {
        class: "movie-info-col"
    });

    var movieTitle = $("<h1>", {
        class: "detail-title",
        text: title + (releaseYear ? " (" + releaseYear + ")" : "")
    });

    var movieRating = $("<div>", {
        class: "detail-rating",
        text: "Rating: " + (rating === 0 ? "N/A" : rating.toFixed(1))
    });

    var movieGenres = $("<div>", {
        class: "detail-genres",
        text: "Genres: " + genres
    });

    var movieRatingCount = $("<div>", {
        class: "detail-rating-count",
        text: "Number of Ratings: " + movie.ratingNumber
    });

    // 组合元素
    posterCol.append(posterImg);
    infoCol.append(movieTitle, movieRating, movieGenres, movieRatingCount);
    movieDetails.append(posterCol, infoCol);
    moviePanel.append(movieDetails);

    // 添加顶级评分
    if (movie.topRatings && movie.topRatings.length > 0) {
        var ratingsSection = $("<div>", {
            class: "top-ratings-section"
        });

        var ratingsTitle = $("<h3>", {
            text: "Top Ratings"
        });

        var ratingsList = $("<div>", {
            class: "ratings-list"
        });

        $.each(movie.topRatings, function (i, rating) {
            var ratingItem = $("<div>", {
                class: "rating-item"
            });

            var userLink = $("<a>", {
                href: "user.html?id=" + rating.userId,
                text: "User " + rating.userId + ": "
            });

            var score = $("<span>", {
                text: rating.score.toFixed(1)
            });

            ratingItem.append(userLink, score);
            ratingsList.append(ratingItem);
        });

        ratingsSection.append(ratingsTitle, ratingsList);
        moviePanel.append(ratingsSection);
    }
}

/**
 * 显示用户信息
 */
function showUserInfo(user, container) {
    if (!user || !user.userId) {
        return;
    }

    var userPanel = $(container);
    userPanel.empty();

    var userId = user.userId;
    var averageRating = user.averageRating;
    var highestRating = user.highestRating;
    var lowestRating = user.lowestRating;
    var ratingCount = user.ratingCount;

    var userInfo = $("<div>", {
        class: "user-info"
    });

    var userAvatar = $("<div>", {
        class: "user-avatar"
    });

    var avatarImg = $("<img>", {
        src: "static/images/user-avatar.png",
        onerror: "this.onerror=null;this.src='static/images/default-avatar.png';",
        class: "avatar-img"
    });

    var infoCol = $("<div>", {
        class: "user-details"
    });

    var userTitle = $("<h1>", {
        class: "user-title",
        text: "User " + userId
    });

    var userAvgRating = $("<div>", {
        class: "user-avg-rating",
        text: "Average Rating: " + averageRating.toFixed(1)
    });

    var userRatingRange = $("<div>", {
        class: "user-rating-range",
        text: "Rating Range: " + lowestRating.toFixed(1) + " - " + highestRating.toFixed(1)
    });

    var userRatingCount = $("<div>", {
        class: "user-rating-count",
        text: "Number of Ratings: " + ratingCount
    });

    // 组合元素
    userAvatar.append(avatarImg);
    infoCol.append(userTitle, userAvgRating, userRatingRange, userRatingCount);
    userInfo.append(userAvatar, infoCol);
    userPanel.append(userInfo);
}

/**
 * 显示用户评分历史
 */
function showUserRatings(user, container) {
    if (!user || !user.userId || !user.ratings || user.ratings.length === 0) {
        return;
    }

    var ratingsPanel = $(container);
    ratingsPanel.empty();

    var ratingsTable = $("<table>", {
        class: "ratings-table"
    });

    var tableHeader = $("<tr>", {
        class: "table-header"
    });

    tableHeader.append(
        $("<th>", { text: "Movie ID" }),
        $("<th>", { text: "Score" }),
        $("<th>", { text: "Date" })
    );

    ratingsTable.append(tableHeader);

    $.each(user.ratings.slice(0, 50), function (i, rating) {
        var ratingRow = $("<tr>");

        var movieLink = $("<a>", {
            href: "movie.html?id=" + rating.movieId + "&model=default",
            text: rating.movieId
        });

        var movieCell = $("<td>");
        movieCell.append(movieLink);

        var scoreCell = $("<td>", {
            text: rating.score.toFixed(1)
        });

        var dateCell = $("<td>", {
            text: new Date(rating.timestamp * 1000).toLocaleDateString()
        });

        ratingRow.append(movieCell, scoreCell, dateCell);
        ratingsTable.append(ratingRow);
    });

    ratingsPanel.append(ratingsTable);
} 