(function () {
  "use strict";

  var root = document.documentElement;
  var themeToggle = document.getElementById("theme-toggle");
  var menuToggle = document.querySelector(".menu-toggle");
  var primaryNav = document.querySelector(".nav-links");
  var navScrim = document.querySelector(".nav-scrim");
  var header = document.querySelector(".site-header");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var coarsePointer = window.matchMedia("(pointer: coarse)");
  var sharedScript = document.currentScript;

  function evaluateXPath(xpath, context) {
    var result = document.evaluate(
      xpath,
      context,
      null,
      XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
      null
    );
    var nodes = [];
    var index;

    for (index = 0; index < result.snapshotLength; index += 1) {
      nodes.push(result.snapshotItem(index));
    }
    return nodes;
  }

  function hasDirectText(element) {
    return Array.prototype.some.call(element.childNodes, function (node) {
      return node.nodeType === Node.TEXT_NODE && node.nodeValue.trim();
    });
  }

  function isIgnoredTypographyNode(element, scope) {
    var ignored = element.closest("script, style, svg, template, noscript, title");
    return ignored && scope.contains(ignored);
  }

  function fallbackTypographyRole(element, scope) {
    var interactive = element.closest("button, input, select, textarea");
    var link = element.closest("a");

    if (interactive && scope.contains(interactive)) return "control";
    if (link && scope.contains(link)) return "control";
    return "body";
  }

  function resolveCustomProperty(name, seen) {
    var visited = seen || {};
    var value;
    var variablePattern;

    if (visited[name]) return "";
    visited[name] = true;
    value = window.getComputedStyle(root).getPropertyValue(name).trim();
    variablePattern = /var\(\s*(--[\w-]+)(?:\s*,[^)]+)?\s*\)/g;

    return value.replace(variablePattern, function (_, nestedName) {
      return resolveCustomProperty(nestedName, visited);
    });
  }

  function lengthToPixels(value) {
    var numeric = Number.parseFloat(value);
    if (!Number.isFinite(numeric)) return null;
    if (value.indexOf("rem") !== -1) {
      return (
        numeric *
        Number.parseFloat(window.getComputedStyle(root).fontSize || "16")
      );
    }
    if (value.indexOf("px") !== -1 || /^-?[\d.]+$/.test(value)) {
      return numeric;
    }
    return null;
  }

  function firstFamily(value) {
    return (value.split(",")[0] || "")
      .replace(/^["']|["']$/g, "")
      .trim()
      .toLowerCase();
  }

  function normalizedColor(value) {
    var color = value.trim().toLowerCase();
    var match;
    var hex;

    if (color.charAt(0) === "#") {
      hex = color.slice(1);
      if (hex.length === 3) {
        hex = hex
          .split("")
          .map(function (character) {
            return character + character;
          })
          .join("");
      }
      if (hex.length === 6) {
        return [
          Number.parseInt(hex.slice(0, 2), 16),
          Number.parseInt(hex.slice(2, 4), 16),
          Number.parseInt(hex.slice(4, 6), 16)
        ].join(",");
      }
    }

    match = color.match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/);
    if (match) {
      return [
        Math.round(Number.parseFloat(match[1])),
        Math.round(Number.parseFloat(match[2])),
        Math.round(Number.parseFloat(match[3]))
      ].join(",");
    }
    return color;
  }

  function auditTypography(contract) {
    var expectations = contract.role_expectations || {};
    var elements = Array.prototype.slice.call(
      document.querySelectorAll("[data-type-role]")
    );
    var errors = [];
    var propertyChecks = 0;
    var propertyPasses = 0;
    var transitionChecks = 0;
    var transitionPasses = 0;
    var roleCounts = {};

    function check(condition, element, property, expected, actual) {
      propertyChecks += 1;
      if (condition) {
        propertyPasses += 1;
        return;
      }
      errors.push({
        actual: actual,
        expected: expected,
        property: property,
        role: element.getAttribute("data-type-role"),
        tag: element.tagName.toLowerCase(),
        text: element.textContent.trim().replace(/\s+/g, " ").slice(0, 72)
      });
    }

    elements.forEach(function (element) {
      var role = element.getAttribute("data-type-role");
      var expectation = expectations[role];
      var style = window.getComputedStyle(element);
      var expectedSize;
      var expectedWeight;
      var expectedFamily;
      var expectedColor;
      var actualSize;
      var lineHeightRatio;
      var activeNavigation;

      roleCounts[role] = (roleCounts[role] || 0) + 1;
      if (!expectation) {
        errors.push({
          property: "role",
          role: role,
          tag: element.tagName.toLowerCase(),
          text: element.textContent.trim().replace(/\s+/g, " ").slice(0, 72)
        });
        return;
      }

      expectedSize = lengthToPixels(
        resolveCustomProperty(expectation.size_token)
      );
      actualSize = Number.parseFloat(style.fontSize);
      check(
        expectedSize !== null && Math.abs(actualSize - expectedSize) <= 0.25,
        element,
        "font-size",
        expectedSize,
        actualSize
      );

      activeNavigation =
        role === "navigation" &&
        (element.classList.contains("is-current") ||
          element.classList.contains("is-active"));
      expectedWeight = resolveCustomProperty(
        activeNavigation && expectation.active_weight_token
          ? expectation.active_weight_token
          : expectation.weight_token
      );
      check(
        String(style.fontWeight) === String(expectedWeight),
        element,
        "font-weight",
        expectedWeight,
        style.fontWeight
      );

      expectedFamily = firstFamily(
        resolveCustomProperty(expectation.family_token)
      );
      check(
        firstFamily(style.fontFamily) === expectedFamily,
        element,
        "font-family",
        expectedFamily,
        firstFamily(style.fontFamily)
      );

      lineHeightRatio =
        Number.parseFloat(style.lineHeight) / Number.parseFloat(style.fontSize);
      check(
        lineHeightRatio >= expectation.line_height_min - 0.01 &&
          lineHeightRatio <= expectation.line_height_max + 0.01,
        element,
        "line-height",
        expectation.line_height_min + "-" + expectation.line_height_max,
        Number(lineHeightRatio.toFixed(3))
      );

      if (expectation.color_token) {
        expectedColor = normalizedColor(
          resolveCustomProperty(expectation.color_token)
        );
        check(
          normalizedColor(style.color) === expectedColor,
          element,
          "color",
          expectedColor,
          normalizedColor(style.color)
        );
      }
    });

    document.querySelectorAll("main h1, main h2, main h3, main h4, main h5, main h6")
      .forEach(function (heading, index, headings) {
        var level = Number.parseInt(heading.tagName.slice(1), 10);
        var parentHeading = null;
        var parentIndex;
        var parentSize;
        var currentSize;

        for (parentIndex = index - 1; parentIndex >= 0; parentIndex -= 1) {
          if (
            Number.parseInt(headings[parentIndex].tagName.slice(1), 10) < level
          ) {
            parentHeading = headings[parentIndex];
            break;
          }
        }
        if (!parentHeading) return;

        transitionChecks += 1;
        parentSize = Number.parseFloat(
          window.getComputedStyle(parentHeading).fontSize
        );
        currentSize = Number.parseFloat(
          window.getComputedStyle(heading).fontSize
        );
        if (currentSize < parentSize) {
          transitionPasses += 1;
        } else {
          errors.push({
            actual: currentSize,
            expected: "< " + parentSize,
            property: "heading-transition",
            role: heading.getAttribute("data-type-role"),
            tag: heading.tagName.toLowerCase(),
            text: heading.textContent.trim().replace(/\s+/g, " ").slice(0, 72)
          });
        }
      });

    return {
      contract: contract.version,
      elements: elements.length,
      errors: errors,
      passed: errors.length === 0,
      propertyChecks: propertyChecks,
      propertyPasses: propertyPasses,
      roleCounts: roleCounts,
      transitionChecks: transitionChecks,
      transitionPasses: transitionPasses
    };
  }

  function applyTypographyContract(contract) {
    var scopes = evaluateXPath(contract.scope_xpath, document);

    scopes.forEach(function (scope) {
      scope.querySelectorAll("[data-type-role]").forEach(function (element) {
        element.removeAttribute("data-type-role");
      });

      contract.roles.forEach(function (rule) {
        evaluateXPath(rule.xpath, scope).forEach(function (element) {
          if (element && element.nodeType === Node.ELEMENT_NODE) {
            element.setAttribute("data-type-role", rule.name);
          }
        });
      });

      scope.querySelectorAll("*").forEach(function (element) {
        if (
          !hasDirectText(element) ||
          isIgnoredTypographyNode(element, scope) ||
          element.closest("[data-type-role]")
        ) {
          return;
        }
        element.setAttribute(
          "data-type-role",
          fallbackTypographyRole(element, scope)
        );
      });

      scope.setAttribute("data-type-contract", contract.version);
    });

    window.DeclareTypography = {
      audit: function () {
        return auditTypography(contract);
      },
      version: contract.version
    };

    document.dispatchEvent(
      new CustomEvent("declare:typography-ready", {
        detail: { version: contract.version }
      })
    );
  }

  function initializeTypographyContract() {
    if (!sharedScript || !window.fetch) return;

    var contractUrl = new URL(
      "../config/typography-contract.json",
      sharedScript.src
    );
    window
      .fetch(contractUrl.toString())
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Unable to load typography contract");
        }
        return response.json();
      })
      .then(applyTypographyContract)
      .catch(function () {
        root.setAttribute("data-type-contract", "structural-fallback");
      });
  }

  function updateThemeControl() {
    if (!themeToggle) return;
    var current = root.getAttribute("data-theme");
    themeToggle.setAttribute(
      "aria-label",
      current === "dark" ? "Use light theme" : "Use dark theme"
    );
  }

  function initializeTheme() {
    if (!themeToggle) return;

    var savedTheme = window.localStorage.getItem("theme");
    if (savedTheme === "light" || savedTheme === "dark") {
      root.setAttribute("data-theme", savedTheme);
    }

    updateThemeControl();
    themeToggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      window.localStorage.setItem("theme", next);
      updateThemeControl();
    });
  }

  function setPrimaryMenu(open) {
    if (!menuToggle || !primaryNav || !navScrim) return;

    primaryNav.classList.toggle("open", open);
    navScrim.classList.toggle("open", open);
    document.body.classList.toggle("menu-open", open);
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  function initializePrimaryMenu() {
    if (!menuToggle || !primaryNav || !navScrim) return;

    menuToggle.addEventListener("click", function () {
      setPrimaryMenu(menuToggle.getAttribute("aria-expanded") !== "true");
    });
    navScrim.addEventListener("click", function () {
      setPrimaryMenu(false);
    });
    primaryNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setPrimaryMenu(false);
      });
    });
    document.addEventListener("keydown", function (event) {
      if (
        event.key === "Escape" &&
        menuToggle.getAttribute("aria-expanded") === "true"
      ) {
        setPrimaryMenu(false);
        menuToggle.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 720) setPrimaryMenu(false);
    });
  }

  function initializeSectionMenus() {
    var menus = Array.prototype.slice.call(
      document.querySelectorAll("[data-section-menu]")
    );
    var updateFrame = null;

    if (!menus.length) return;

    function getScroller(menu) {
      return menu.querySelector("[data-section-menu-scroll]") || menu;
    }

    function getLinks(menu) {
      return Array.prototype.slice.call(menu.querySelectorAll('a[href^="#"]'));
    }

    function getSection(link) {
      var hash = link.getAttribute("href");
      if (!hash || hash === "#") return null;

      try {
        return document.getElementById(decodeURIComponent(hash.slice(1)));
      } catch (error) {
        return null;
      }
    }

    /*
     * A section that the page has filtered away is not navigable, so its menu
     * entry is withdrawn rather than left pointing at nothing. Without this, a
     * publication list filtered to one topic still offered every year in the
     * rail and most of those links moved nowhere.
     */
    function isSectionAvailable(section) {
      if (!section) return false;
      if (section.hasAttribute("hidden")) return false;
      return section.getClientRects().length > 0;
    }

    function syncLinkAvailability(menu) {
      var anyHidden = false;
      getLinks(menu).forEach(function (link) {
        var available = isSectionAvailable(getSection(link));
        link.hidden = !available;
        link.setAttribute("aria-hidden", available ? "false" : "true");
        if (available) link.removeAttribute("tabindex");
        else link.setAttribute("tabindex", "-1");
        if (!available) anyHidden = true;
      });
      menu.classList.toggle("section-menu--filtered", anyHidden);
    }

    function isVisible(menu) {
      return menu.getClientRects().length > 0;
    }

    function isHorizontal(menu) {
      var scroller = getScroller(menu);
      var style = window.getComputedStyle(scroller);
      return (
        menu.classList.contains("section-menu--inline") ||
        (style.display === "flex" && style.flexDirection !== "column")
      );
    }

    function isHorizontallyScrollable(menu) {
      var scroller = getScroller(menu);
      return (
        isHorizontal(menu) &&
        scroller.clientWidth > 0 &&
        scroller.scrollWidth > scroller.clientWidth + 2
      );
    }

    function getHeaderBottom() {
      return header ? header.getBoundingClientRect().bottom : 0;
    }

    function getStickyLine(menu) {
      var computedTop = Number.parseFloat(window.getComputedStyle(menu).top) || 0;
      return Math.max(getHeaderBottom() + 18, computedTop + 1);
    }

    function updateDockedState(menu, sections) {
      var rect = menu.getBoundingClientRect();
      var stickyLine = getStickyLine(menu);
      var docked = rect.top <= stickyLine;

      if (menu.hasAttribute("data-section-menu-bounded") && sections.length) {
        var lastRect = sections[sections.length - 1].getBoundingClientRect();
        docked = docked && lastRect.bottom > stickyLine + rect.height;
      }

      menu.classList.toggle("is-stuck", docked);
      menu.classList.toggle("is-docked", docked);
      return docked;
    }

    function getReadingLine(menu, docked) {
      var line = getHeaderBottom() + 24;
      if (docked && isHorizontal(menu)) {
        line = Math.max(line, menu.getBoundingClientRect().bottom + 18);
      }
      return Math.round(line);
    }

    function getDockedMenuBottom(menu) {
      var rect = menu.getBoundingClientRect();
      var computedTop = parseFloat(window.getComputedStyle(menu).top);
      var stickyTop = Number.isFinite(computedTop)
        ? computedTop
        : getHeaderBottom() + 16;

      return stickyTop + rect.height;
    }

    function revealCurrentLink(menu, link) {
      var scroller = getScroller(menu);
      if (!link || !isHorizontallyScrollable(menu)) return;

      var scrollerRect = scroller.getBoundingClientRect();
      var linkRect = link.getBoundingClientRect();
      var edge = 12;
      var targetLeft = null;

      if (linkRect.left < scrollerRect.left + edge) {
        targetLeft =
          scroller.scrollLeft + linkRect.left - scrollerRect.left - edge;
      } else if (linkRect.right > scrollerRect.right - edge) {
        targetLeft =
          scroller.scrollLeft + linkRect.right - scrollerRect.right + edge;
      }

      if (targetLeft === null) return;

      scroller.scrollTo({
        left: Math.max(0, targetLeft),
        behavior:
          reducedMotion.matches || coarsePointer.matches ? "auto" : "smooth"
      });
    }

    function setCurrentLink(menu, current) {
      if (!current || menu._sectionMenuCurrent === current) return;

      getLinks(menu).forEach(function (link) {
        var isCurrent = link === current;
        link.classList.toggle("is-current", isCurrent);
        link.classList.toggle("is-active", isCurrent);
        if (isCurrent) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });

      menu._sectionMenuCurrent = current;
      revealCurrentLink(menu, current);
    }

    function updateMenu(menu) {
      if (!isVisible(menu)) return;

      syncLinkAvailability(menu);

      var pairs = getLinks(menu)
        .map(function (link) {
          return { link: link, section: getSection(link) };
        })
        .filter(function (pair) {
          return isSectionAvailable(pair.section);
        });

      if (!pairs.length) return;

      var sections = pairs.map(function (pair) {
        return pair.section;
      });
      var docked = updateDockedState(menu, sections);
      var readingLine = getReadingLine(menu, docked);
      var current = pairs[0].link;
      var currentTop = Number.NEGATIVE_INFINITY;
      var hash = window.location.hash;

      pairs.forEach(function (pair) {
        var sectionTop = pair.section.getBoundingClientRect().top;
        if (sectionTop > readingLine + 2) return;

        if (sectionTop > currentTop + 4) {
          current = pair.link;
          currentTop = sectionTop;
          return;
        }

        if (
          Math.abs(sectionTop - currentTop) <= 4 &&
          pair.link.getAttribute("href") === hash
        ) {
          current = pair.link;
        }
      });

      if (
        Math.ceil(window.scrollY + window.innerHeight) >=
        document.documentElement.scrollHeight - 2
      ) {
        current = pairs[pairs.length - 1].link;
      }

      if (menu._sectionMenuLocked) current = menu._sectionMenuLocked;
      setCurrentLink(menu, current);
    }

    function updateAllMenus() {
      menus.forEach(updateMenu);
      updateFrame = null;
    }

    function requestMenuUpdate() {
      if (!updateFrame) {
        updateFrame = window.requestAnimationFrame(updateAllMenus);
      }
    }

    function releaseClickLockWhenSettled(menu) {
      if (menu._sectionMenuSettleFrame) {
        window.cancelAnimationFrame(menu._sectionMenuSettleFrame);
      }

      var previousY = window.scrollY;
      var stableFrames = 0;
      var elapsedFrames = 0;

      function checkPosition() {
        var currentY = window.scrollY;
        stableFrames =
          Math.abs(currentY - previousY) < 0.5 ? stableFrames + 1 : 0;
        previousY = currentY;
        elapsedFrames += 1;

        if (stableFrames >= 4 || elapsedFrames >= 180) {
          menu._sectionMenuLocked = null;
          menu._sectionMenuSettleFrame = null;
          requestMenuUpdate();
          return;
        }

        menu._sectionMenuSettleFrame =
          window.requestAnimationFrame(checkPosition);
      }

      menu._sectionMenuSettleFrame = window.requestAnimationFrame(checkPosition);
    }

    function getTargetTop(menu, section) {
      var targetOffset = getHeaderBottom() + 24;
      var targetTop;

      if (isHorizontal(menu)) {
        targetOffset = Math.max(
          targetOffset,
          getDockedMenuBottom(menu) + 18
        );
      }

      targetTop = Math.max(
        0,
        window.scrollY + section.getBoundingClientRect().top - targetOffset
      );

      if (
        isHorizontal(menu) &&
        menu.getBoundingClientRect().top > getStickyLine(menu)
      ) {
        targetTop = Math.max(
          targetTop,
          window.scrollY +
            menu.getBoundingClientRect().top -
            getStickyLine(menu) +
            1
        );
      }

      return targetTop;
    }

    function prepareMenuForNavigation(menu) {
      if (!isHorizontal(menu)) return;
      menu.classList.add("is-stuck");
      menu.classList.add("is-docked");
    }

    function scrollInstantly(top) {
      var previousBehavior = root.style.scrollBehavior;
      root.style.scrollBehavior = "auto";
      window.scrollTo({ top: top, behavior: "auto" });
      root.style.scrollBehavior = previousBehavior;
    }

    function handleMenuClick(menu, link, event) {
      var section = getSection(link);
      if (
        !section ||
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }

      event.preventDefault();
      prepareMenuForNavigation(menu);
      menu._sectionMenuLocked = link;
      setCurrentLink(menu, link);
      window.history.pushState(null, "", link.getAttribute("href"));

      if (reducedMotion.matches) {
        scrollInstantly(getTargetTop(menu, section));
      } else {
        window.scrollTo({
          top: getTargetTop(menu, section),
          behavior: "smooth"
        });
      }
      releaseClickLockWhenSettled(menu);
    }

    function syncInitialHash() {
      if (!window.location.hash) return;

      var matchedMenu = null;
      var matchedLink = null;
      menus.some(function (menu) {
        if (!isVisible(menu)) return false;
        matchedLink = getLinks(menu).find(function (link) {
          return link.getAttribute("href") === window.location.hash;
        });
        if (!matchedLink) return false;
        matchedMenu = menu;
        return true;
      });

      if (!matchedMenu || !matchedLink) return;
      var section = getSection(matchedLink);
      if (!section) return;

      prepareMenuForNavigation(matchedMenu);
      matchedMenu._sectionMenuLocked = matchedLink;
      setCurrentLink(matchedMenu, matchedLink);
      window.requestAnimationFrame(function () {
        scrollInstantly(getTargetTop(matchedMenu, section));
        matchedMenu._sectionMenuLocked = null;
        requestMenuUpdate();
      });
    }

    menus.forEach(function (menu) {
      getLinks(menu).forEach(function (link) {
        link.addEventListener("click", function (event) {
          handleMenuClick(menu, link, event);
        });
      });
    });

    updateAllMenus();
    syncInitialHash();
    window.addEventListener("scroll", requestMenuUpdate, { passive: true });
    window.addEventListener("resize", requestMenuUpdate);

    /*
     * Filtering a list toggles `hidden` on its sections without scrolling, so
     * no scroll or resize event would tell the menu that its targets changed.
     * Watch the sections the menus point at and refresh when they appear or
     * disappear.
     */
    if (typeof window.MutationObserver === "function") {
      var watched = [];
      menus.forEach(function (menu) {
        getLinks(menu).forEach(function (link) {
          var section = getSection(link);
          if (section && watched.indexOf(section) === -1) watched.push(section);
        });
      });

      if (watched.length) {
        var availabilityObserver = new window.MutationObserver(requestMenuUpdate);
        watched.forEach(function (section) {
          availabilityObserver.observe(section, {
            attributes: true,
            attributeFilter: ["hidden", "style", "class"],
          });
        });
      }
    }
    window.addEventListener("load", function () {
      if (window.location.hash) syncInitialHash();
      else requestMenuUpdate();
    });
    window.addEventListener("hashchange", syncInitialHash);

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        if (window.location.hash) syncInitialHash();
        else requestMenuUpdate();
      });
    }
  }

  initializeTheme();
  initializeTypographyContract();
  initializePrimaryMenu();
  initializeSectionMenus();
})();
