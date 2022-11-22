(function() {
    function getCookie(cname) {
        let name = cname + "=";
        let decodedCookie = decodeURIComponent(document.cookie);
        let ca = decodedCookie.split(';');
        for(let i = 0; i <ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "[]";
    }

    let elements_list = JSON.parse(getCookie("targets"));

    let $ = jQuery;

    function getTransform(from, to) {
        let A, H, b, h, i, k, k_i, l, lhs, m, ref, rhs;
        console.assert((from.length === (ref = to.length) && ref === 4));
        A = []; // 8x8
        for (i = k = 0; k < 4; i = ++k) {
            A.push([from[i].x, from[i].y, 1, 0, 0, 0, -from[i].x * to[i].x, -from[i].y * to[i].x]);
            A.push([0, 0, 0, from[i].x, from[i].y, 1, -from[i].x * to[i].y, -from[i].y * to[i].y]);
        }
        b = []; // 8x1
        for (i = l = 0; l < 4; i = ++l) {
            b.push(to[i].x);
            b.push(to[i].y);
        }
        // Solve A * h = b for h
        h = numeric.solve(A, b);
        H = [[h[0], h[1], 0, h[2]], [h[3], h[4], 0, h[5]], [0, 0, 1, 0], [h[6], h[7], 0, 1]];
        // Sanity check that H actually maps `from` to `to`
        for (i = m = 0; m < 4; i = ++m) {
            lhs = numeric.dot(H, [from[i].x, from[i].y, 0, 1]);
            k_i = lhs[3];
            rhs = numeric.dot(k_i, [to[i].x, to[i].y, 0, 1]);
            console.assert(numeric.norm2(numeric.sub(lhs, rhs)) < 1e-9, "Not equal:", lhs, rhs);
        }
        return H;
    };

    function applyTransform(element, originalPos, targetPos, idx, is_stop, callback) {
        if(targetPos == null) {
            if(!!elements_list[idx]) {
                targetPos = elements_list[idx];
            } else {
                targetPos = originalPos;
            }
        }

        var from, i, j, p, to;
        // All offsets were calculated relative to the document
        // Make them relative to (0, 0) of the element instead
        from = (function() {
            var k, len, results;
            results = [];
            for (k = 0, len = originalPos.length; k < len; k++) {
                p = originalPos[k];
                results.push({
                    x: p[0] - originalPos[0][0],
                    y: p[1] - originalPos[0][1]
                });
            }
            return results;
        })();
        to = (function() {
            var k, len, results;
            results = [];
            for (k = 0, len = targetPos.length; k < len; k++) {
                p = targetPos[k];
                results.push({
                    x: p[0] - originalPos[0][0],
                    y: p[1] - originalPos[0][1]
                });
            }
            return results;
        })();
        // Solve for the transform
        let H = getTransform(from, to);
        
        // Apply the matrix3d as H transposed because matrix3d is column major order
        // Also need use toFixed because css doesn't allow scientific notation
        $(element).css({
            'transform': `matrix3d(${((function() {
                var k, results;
                results = [];
                for (i = k = 0; k < 4; i = ++k) {
                    results.push((function() {
                        var l, results1;
                        results1 = [];
                        for (j = l = 0; l < 4; j = ++l) {
                            results1.push(H[j][i].toFixed(20));
                        }
                        return results1;
                    })());
                }
                return results;
            })()).join(',')})`,
            'transform-origin': '0 0'
        });

        elements_list[idx] = targetPos;

        if(typeof callback === "function" && is_stop) {
            callback();
        }
    };

    function makeTransformable(selector, callback) {
        let res = [];

        $(selector).each(function(i, element) {
            var controlPoints, originalPos, p, position;
            $(element).css('transform', '');
            
            // Add four dots to corners of `element` as control points
            controlPoints = (function() {
                var k, len, ref, results;
                ref = ['left top', 'left bottom', 'right top', 'right bottom'];
                results = [];
                for (k = 0, len = ref.length; k < len; k++) {
                    position = ref[k];
                    results.push($('<div>').css({
                        border: '10px solid black',
                        borderRadius: '10px',
                        cursor: 'move',
                        position: 'absolute',
                        zIndex: 100000
                    }).appendTo('body').position({
                        at: position,
                        of: element,
                        collision: 'none'
                    }));
                }
                return results;
            })();
            // Record the original positions of the dots
            originalPos = (function() {
                var k, len, results;
                results = [];
                for (k = 0, len = controlPoints.length; k < len; k++) {
                    p = controlPoints[k];
                    results.push([p.offset().left, p.offset().top]);
                }
                return results;
            })();

            applyTransform(element, originalPos, null, i, false, callback);
            
            // Transform `element` to match the new positions of the dots whenever dragged
            $(controlPoints).draggable({
                start: () => {
                    return $(element).css('pointer-events', 'none'); // makes dragging around iframes easier 
                },
                drag: () => {
                    return applyTransform(element, originalPos, (function() {
                        var k, len, results;
                        results = [];
                        for (k = 0, len = controlPoints.length; k < len; k++) {
                            p = controlPoints[k];
                            results.push([p.offset().left, p.offset().top]);
                        }
                        return results;
                    })(), i, false, callback);
                },
                stop: () => {
                    applyTransform(element, originalPos, (function() {
                        var k, len, results;
                        results = [];
                        for (k = 0, len = controlPoints.length; k < len; k++) {
                            p = controlPoints[k];
                            results.push([p.offset().left, p.offset().top]);
                        }
                        return results;
                    })(), i, true, callback);
                    return $(element).css('pointer-events', 'auto');
                }
            });

            res.push(null);
        });

        return res;
    };

    makeTransformable('.box', function() {
        console.log(elements_list);
        document.cookie = "targets=" + JSON.stringify(elements_list) + "; path=/";
    });

}).call(this);