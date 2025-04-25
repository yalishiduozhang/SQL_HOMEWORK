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

    if (movie.ratingNumber > 0) {
        var ratingsSection = $("<div>", {
            class: "ratings-distribution-section"
        });
    
        var ratingsTitle = $("<h3>", {
            text: "评分占比"
        });
        
        // 计算评分分布 - 使用高斯分布近似
        var distributionContainer = $("<div>", {
            class: "rating-distribution-container"
        });
        
        // 基于平均评分和总评分数生成合理的分布数据
        var mean = movie.averageRating;
        // 假设分布为正态分布，标准差设为合理值
        var stdDev = 0.8; 
        
        // 预定义的评分档位
        var ratingLevels = ["5", "4.5", "4", "3.5", "3", "2.5", "2", "1.5", "1", "0.5"];
        
        // 计算每个评分档位的占比
        var ratingDistribution = {};
        var totalPercentage = 0;
        
        // 使用正态分布来估算各评分比例
        for (var i = 0; i < ratingLevels.length; i++) {
            var score = parseFloat(ratingLevels[i]);
            // 计算每个评分的概率密度
            var percentage = calculateNormalDistribution(score, mean, stdDev);
            ratingDistribution[ratingLevels[i]] = percentage;
            totalPercentage += percentage;
        }
        
        // 归一化百分比
        for (var rating in ratingDistribution) {
            ratingDistribution[rating] = (ratingDistribution[rating] / totalPercentage) * 100;
        }
        
        // 创建评分分布条形图
        $.each(ratingLevels, function(i, score) {
            var percentage = ratingDistribution[score].toFixed(1);
            
            // 将整行包装在可点击的div中
            var ratingRowLink = $("<div>", {
                class: "rating-row-link",
                "data-movie-id": movie.movieId,
                "data-score": score,
                title: "点击查看所有 " + score + " 星评价"
            }).click(function() {
                var clickedMovieId = $(this).data("movie-id");
                var clickedScore = $(this).data("score");
                showRatingsByScore(clickedMovieId, clickedScore);
            });
            
            var ratingRow = $("<div>", {
                class: "rating-distribution-row"
            });
            
            var ratingLabel = $("<div>", {
                class: "rating-label",
                text: score + " 星"
            });
            
            var ratingBarContainer = $("<div>", {
                class: "rating-bar-container"
            });
            
            var ratingBar = $("<div>", {
                class: "rating-bar",
                style: "width: " + percentage + "%"
            });
            
            var ratingPercentage = $("<div>", {
                class: "rating-percentage",
                text: percentage + "%"
            });
            
            ratingBarContainer.append(ratingBar);
            ratingRow.append(ratingLabel, ratingBarContainer, ratingPercentage);
            ratingRowLink.append(ratingRow);
            distributionContainer.append(ratingRowLink);
        });
        
        // 添加说明文字
        var distributionNote = $("<div>", {
            class: "distribution-note",
            text: "注：此评分占比基于总体评分分布模型估算，共 " + movie.ratingNumber + " 条评分"
        });
        
        ratingsSection.append(ratingsTitle, distributionContainer, distributionNote);
        moviePanel.append(ratingsSection);
        
        // 添加评分分布样式
        if ($("#rating-distribution-styles").length === 0) {
            $("<style>", { id: "rating-distribution-styles" })
                .text(`
                    .ratings-distribution-section { margin-top: 30px; }
                    .rating-distribution-container { margin-top: 15px; }
                    .rating-distribution-row { display: flex; align-items: center; margin-bottom: 8px; }
                    .rating-label { width: 60px; text-align: right; margin-right: 10px; }
                    .rating-bar-container { flex-grow: 1; background-color: #f0f0f0; height: 20px; border-radius: 4px; overflow: hidden; }
                    .rating-bar { height: 100%; background-color: #ffad33; }
                    .rating-percentage { width: 60px; margin-left: 10px; }
                    .distribution-note { font-size: 12px; color: #666; margin-top: 10px; font-style: italic; }
                `)
                .appendTo("head");
        }
    }
    
    // 正态分布计算函数
    function calculateNormalDistribution(x, mean, stdDev) {
        return Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
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
        src: "static/images/avatar/" + (userId % 10) + ".png",
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

    // 按时间戳排序评分
    var sortedRatings = user.ratings.slice().sort(function(a, b) {
        return b.timestamp - a.timestamp; // 降序排列，最新的评分在前
    });

    // 分页设置
    var pageSize = 20; // 每页显示20条评分
    var totalPages = Math.ceil(sortedRatings.length / pageSize);
    var currentPage = 1; // 默认显示第一页

    // 添加分页样式 - 确保样式只添加一次
    if ($("#ratings-pagination-styles").length === 0) {
        $("<style>", { id: "ratings-pagination-styles" })
            .text(`
                .pagination { margin-top: 20px; text-align: center; }
                .page-btn { padding: 5px 10px; margin: 0 5px; cursor: pointer; }
                .page-btn.disabled { opacity: 0.5; cursor: not-allowed; }
                .page-select { padding: 5px; margin: 0 5px; }
                .ratings-page-info { margin-bottom: 10px; font-weight: bold; }
                .page-text { vertical-align: middle; }
            `)
            .appendTo("head");
    }

    function renderPage(page) {
        currentPage = page;
        ratingsPanel.empty();
        
        // 创建评分表格
        var ratingsTable = $("<table>", {
            class: "ratings-table"
        });

        var tableHeader = $("<tr>", {
            class: "table-header"
        });

        tableHeader.append(
            $("<th>", { text: "Movie" }),
            $("<th>", { text: "Score" }),
            $("<th>", { text: "Date" })
        );

        ratingsTable.append(tableHeader);
        
        // 计算当前页的评分范围
        var start = (page - 1) * pageSize;
        var end = Math.min(start + pageSize, sortedRatings.length);
        
        // 显示当前页的评分
        for (var i = start; i < end; i++) {
            var rating = sortedRatings[i];
            var ratingRow = $("<tr>");

            var movieLink = $("<a>", {
                href: "movie.html?id=" + rating.movieId + "&model=default",
                text: rating.title || ("Movie " + rating.movieId)
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
        }
        
        // 显示评分总数和当前页信息
        var pageInfo = $("<div>", {
            class: "ratings-page-info",
            text: "显示 " + (start + 1) + " - " + end + " 条，共 " + sortedRatings.length + " 条评分"
        });
        
        // 创建分页导航
        var pagination = $("<div>", {
            class: "pagination"
        });
        
        // 上一页按钮
        var prevButton = $("<button>", {
            text: "上一页",
            class: "page-btn" + (currentPage === 1 ? " disabled" : ""),
            disabled: currentPage === 1
        }).click(function() {
            if (currentPage > 1) {
                renderPage(currentPage - 1);
            }
        });
        
        // 下一页按钮
        var nextButton = $("<button>", {
            text: "下一页",
            class: "page-btn" + (currentPage === totalPages ? " disabled" : ""),
            disabled: currentPage === totalPages
        }).click(function() {
            if (currentPage < totalPages) {
                renderPage(currentPage + 1);
            }
        });
        
        // 页码选择器
        var pageSelect = $("<select>", {
            class: "page-select"
        }).change(function() {
            renderPage(parseInt($(this).val()));
        });
        
        for (var p = 1; p <= totalPages; p++) {
            var option = $("<option>", {
                value: p,
                text: "第 " + p + " 页",
                selected: p === currentPage
            });
            pageSelect.append(option);
        }
        
        // 组装分页控件
        pagination.append(
            prevButton,
            $("<span>", { text: " 页码: ", class: "page-text" }),
            pageSelect,
            $("<span>", { text: " / " + totalPages + " ", class: "page-text" }),
            nextButton
        );
        
        // 添加到面板
        ratingsPanel.append(pageInfo, ratingsTable, pagination);
    }
    
    // 渲染第一页
    renderPage(1);
}

/**
 * 显示电影的所有评分
 */
function showAllMovieRatings(movieId, page) {
    var ratingsContainer = $('#movieRatings');
    var paginationContainer = $('#ratingsPagination');
    
    ratingsContainer.html('<div class="ratings-loading">正在加载评分数据...</div>');
    
    $.getJSON(baseUrl + 'getmovieratings?id=' + movieId + '&page=' + page, function(data) {
        if (!data || !data.ratings || data.ratings.length === 0) {
            ratingsContainer.html('<div class="no-results"><p>该电影暂无评价</p></div>');
            return;
        }
        
        ratingsContainer.empty();
        
        // 创建评分表格
        var ratingsTable = $("<table>", {
            class: "ratings-table"
        });
        
        var tableHeader = $("<tr>", {
            class: "table-header"
        });
        
        tableHeader.append(
            $("<th>", { text: "用户" }),
            $("<th>", { text: "评分" }),
            $("<th>", { text: "日期" }),
            $("<th>", { text: "评论" })
        );
        
        ratingsTable.append(tableHeader);
        
        // 添加评分行
        $.each(data.ratings, function(i, rating) {
            var ratingRow = $("<tr>");
            
            // 用户列
            var userCell = $("<td>");
            var userLink = $("<a>", {
                href: "user.html?id=" + rating.user_id,
                text: rating.username || ("用户 " + rating.user_id)
            });
            userCell.append(userLink);
            
            // 评分列
            var scoreCell = $("<td>");
            var scoreSpan = $("<span>", {
                class: rating.rating === 5 ? "perfect-score" : "regular-score",
                text: rating.rating + ".0"
            });
            scoreCell.append(scoreSpan);
            
            // 日期列
            var dateCell = $("<td>");
            if (rating.timestamp) {
                var date = new Date(rating.timestamp * 1000);
                dateCell.text(date.toLocaleDateString());
            } else {
                dateCell.text("未知");
            }
            
            // 评论列
            var commentCell = $("<td>");
            commentCell.text(rating.comment || "");
            
            ratingRow.append(userCell, scoreCell, dateCell, commentCell);
            ratingsTable.append(ratingRow);
        });
        
        ratingsContainer.append(ratingsTable);
        
        // 创建分页控件
        createPagination(data, paginationContainer, movieId);
    }).fail(function() {
        ratingsContainer.html('<div class="no-results"><p>加载评分数据失败，请稍后再试</p></div>');
    });
}

/**
 * 创建分页控件
 */
function createPagination(data, container, movieId) {
    container.empty();
    
    if (data.pages <= 1) {
        return;
    }
    
    // 创建页码选择器
    var pageSelect = $("<select>", {
        class: "page-select"
    }).change(function() {
        showAllMovieRatings(movieId, parseInt($(this).val()));
    });
    
    for (var p = 1; p <= data.pages; p++) {
        var option = $("<option>", {
            value: p,
            text: "第 " + p + " 页",
            selected: p === data.page
        });
        pageSelect.append(option);
    }
    
    // 上一页按钮
    var prevButton = $("<button>", {
        text: "上一页",
        class: "page-btn" + (data.page === 1 ? " disabled" : ""),
        disabled: data.page === 1
    }).click(function() {
        if (data.page > 1) {
            showAllMovieRatings(movieId, data.page - 1);
        }
    });
    
    // 下一页按钮
    var nextButton = $("<button>", {
        text: "下一页",
        class: "page-btn" + (data.page === data.pages ? " disabled" : ""),
        disabled: data.page === data.pages
    }).click(function() {
        if (data.page < data.pages) {
            showAllMovieRatings(movieId, data.page + 1);
        }
    });
    
    // 显示总数信息
    var pageInfo = $("<div>", {
        class: "ratings-page-info",
        text: "共 " + data.total + " 条评分，共 " + data.pages + " 页"
    });
    
    // 组装分页控件
    container.append(
        pageInfo,
        $("<div>", { class: "pagination-controls" }).append(
            prevButton,
            $("<span>", { text: " 页码: ", class: "page-text" }),
            pageSelect,
            $("<span>", { text: " / " + data.pages + " 页 ", class: "page-text" }),
            nextButton
        )
    );
}

/**
 * 显示特定评分的所有用户评价
 */
function showRatingsByScore(movieId, score) {
    // 创建模态框
    var modal = $("<div>", {
        class: "rating-modal"
    });
    
    var modalContent = $("<div>", {
        class: "rating-modal-content"
    });
    
    var closeBtn = $("<span>", {
        class: "rating-modal-close",
        html: "&times;"
    }).click(function() {
        modal.remove();
    });
    
    var modalHeader = $("<div>", {
        class: "rating-modal-header"
    });
    
    var modalTitle = $("<h3>", {
        text: score + " 星评价"
    });
    
    var ratingsContainer = $("<div>", {
        class: "rating-modal-body"
    });
    
    var paginationContainer = $("<div>", {
        class: "rating-modal-pagination"
    });
    
    modalHeader.append(modalTitle);
    modalContent.append(closeBtn, modalHeader, ratingsContainer, paginationContainer);
    modal.append(modalContent);
    
    // 添加到页面
    $("body").append(modal);
    
    // 加载特定评分的数据
    loadRatingsByScore(movieId, score, 1, ratingsContainer, paginationContainer);
    
    // 显示模态框
    setTimeout(function() {
        modal.addClass("show");
    }, 10);
}

/**
 * 加载特定评分的用户评价
 */
function loadRatingsByScore(movieId, score, page, container, paginationContainer) {
    container.html('<div class="ratings-loading">正在加载评分数据...</div>');
    
    $.getJSON(baseUrl + 'getmovieratingsbyscore?id=' + movieId + '&score=' + score + '&page=' + page, function(data) {
        if (!data || !data.ratings || data.ratings.length === 0) {
            container.html('<div class="no-results"><p>此评分暂无用户评价</p></div>');
            return;
        }
        
        container.empty();
        
        // 创建评分表格
        var ratingsTable = $("<table>", {
            class: "ratings-table"
        });
        
        var tableHeader = $("<tr>", {
            class: "table-header"
        });
        
        tableHeader.append(
            $("<th>", { text: "用户" }),
            $("<th>", { text: "日期" }),
            $("<th>", { text: "评论" })
        );
        
        ratingsTable.append(tableHeader);
        
        // 添加评分行
        $.each(data.ratings, function(i, rating) {
            var ratingRow = $("<tr>");
            
            // 用户列
            var userCell = $("<td>");
            var userLink = $("<a>", {
                href: "user.html?id=" + rating.user_id,
                text: rating.username || ("用户 " + rating.user_id)
            });
            userCell.append(userLink);
            
            // 日期列
            var dateCell = $("<td>");
            if (rating.timestamp) {
                var date = new Date(rating.timestamp * 1000);
                dateCell.text(date.toLocaleDateString());
            } else {
                dateCell.text("未知");
            }
            
            // 评论列
            var commentCell = $("<td>");
            commentCell.text(rating.comment || "");
            
            ratingRow.append(userCell, dateCell, commentCell);
            ratingsTable.append(ratingRow);
        });
        
        container.append(ratingsTable);
        
        // 创建分页控件
        createRatingsByScorePagination(data, paginationContainer, movieId, score);
    }).fail(function() {
        container.html('<div class="no-results"><p>加载评分数据失败，请稍后再试</p></div>');
    });
}

/**
 * 为特定评分创建分页控件
 */
function createRatingsByScorePagination(data, container, movieId, score) {
    container.empty();
    
    if (data.pages <= 1) {
        return;
    }
    
    // 创建页码选择器
    var pageSelect = $("<select>", {
        class: "page-select"
    }).change(function() {
        loadRatingsByScore(movieId, score, parseInt($(this).val()), 
                          $(".rating-modal-body"), $(".rating-modal-pagination"));
    });
    
    for (var p = 1; p <= data.pages; p++) {
        var option = $("<option>", {
            value: p,
            text: "第 " + p + " 页",
            selected: p === data.page
        });
        pageSelect.append(option);
    }
    
    // 上一页按钮
    var prevButton = $("<button>", {
        text: "上一页",
        class: "page-btn" + (data.page === 1 ? " disabled" : ""),
        disabled: data.page === 1
    }).click(function() {
        if (data.page > 1) {
            loadRatingsByScore(movieId, score, data.page - 1, 
                              $(".rating-modal-body"), $(".rating-modal-pagination"));
        }
    });
    
    // 下一页按钮
    var nextButton = $("<button>", {
        text: "下一页",
        class: "page-btn" + (data.page === data.pages ? " disabled" : ""),
        disabled: data.page === data.pages
    }).click(function() {
        if (data.page < data.pages) {
            loadRatingsByScore(movieId, score, data.page + 1, 
                              $(".rating-modal-body"), $(".rating-modal-pagination"));
        }
    });
    
    // 显示总数信息
    var pageInfo = $("<div>", {
        class: "ratings-page-info",
        text: "共有 " + data.total + " 位用户给出了 " + score + " 星评价"
    });
    
    // 组装分页控件
    container.append(
        pageInfo,
        $("<div>", { class: "pagination-controls" }).append(
            prevButton,
            $("<span>", { text: " 页码: ", class: "page-text" }),
            pageSelect,
            $("<span>", { text: " / " + data.pages + " 页 ", class: "page-text" }),
            nextButton
        )
    );
}