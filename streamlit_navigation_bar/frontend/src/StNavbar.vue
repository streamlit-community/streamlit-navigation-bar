<template>
  <section>
  <link rel="stylesheet"
    type="text/css"
    href="https://fonts.googleapis.com/icon?family=Material+Icons"
  />

  <link
    v-for="link in args.links"
    rel="stylesheet"
    type="text/css"
    :href="link"
  />

  <component v-if="css" :is="'style'">
      {{ css }}
  </component>

  <nav
      class="navbar"
      :style="parseStyles(styles['nav'])">
    <div
      class="navbar-left navbar-group"
      :style="parseStyles(styles['div'])">
      <ul :style="parseStyles(styles['ul'])"
	class="navbar-list">
        <li
          v-if="args.base64_svg"
          :style="parseStyles(styles['li'])"
	  class="navbar-item"
        >
          <a
            v-if="args.logo_page"
            href="#"
	    class="navbar-anchor"
            :style="parseStyles(styles['a'])"
            @click="onClicked(args.logo_page)"
          >
            <img
              :src="`data:image/svg+xml; base64, ${args.base64_svg}`"
              :style="parseStyles(styles['img'])"
            />
          </a>
          <a
            v-else-if="args.logo_page === null"
	    class="navbar-anchor"
            :style="parseStyles(styles['a'])"
          >
            <img
	      class="navbar-logo"
              :src="`data:image/svg+xml; base64, ${args.base64_svg}`"
              :style="parseStyles(styles['img'])"
            />
          </a>
        </li>
        <li
          v-for="page in args.left"
	  class="navbar-item"
          :key="page.title"
          :style="parseStyles(styles['li'])"
        >
          <a
            :href="page.url[0]"
            :target="page.url[1]"
            :style="parseStyles(styles['a'])"
	    class="navbar-anchor"
            @click="onClicked(page)"
          >
            <span
              :data-text="page.title"
              :class="[{active: page.key === activePage}, hoverColor, hoverBgColor]"
              :style="parseStyles(styles['span']) + parseStyles(styles['active'], page.key === activePage)"
	      class="navbar-span"
	      style="display: inline-block;"
            >
              <div
                v-if="page.icon"
                class="material-icons navbar-icon"
                style="display: inline; vertical-align: middle"
              >
                {{ page.icon }}
	      </div>
              <div class="navbar-text" style="display: inline; vertical-align: middle; margin-left: 0.35em">
	        {{ page.title }}
              </div>
            </span>
          </a>
        </li>
      </ul>
    </div>
    <div
      v-if="args.right.length"
      class="navbar-right navbar-group"
      :style="parseStyles(styles['div'])">
      <ul :style="parseStyles(styles['ul'])"
	class="navbar-list">
        <li
          v-for="page in args.right"
	  class="navbar-item"
          :key="page.title"
          :style="parseStyles(styles['li'])"
        >
          <a
            :href="page.url[0]"
            :target="page.url[1]"
            :style="parseStyles(styles['a'])"
	    class="navbar-anchor"
            @click="onClicked(page)"
          >
            <span
              :data-text="page.title"
              :class="[{active: page.key === activePage}, hoverColor, hoverBgColor]"
              :style="parseStyles(styles['span']) + parseStyles(styles['active'], page.key === activePage)"
	      class="navbar-span"
	      style="display: inline-block"
            >
              <div
                v-if="page.icon"
                class="material-icons navbar-icon"
                style="display: inline; vertical-align: middle"
              >
                {{ page.icon }}
              </div>
	      <div class="navbar-text" style="display: inline; vertical-align: middle; margin-left: 0.35em"
              >
              {{ page.title }}
              </div>
            </span>
          </a>
        </li>
      </ul>
    </div>
  </nav>
  </section>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { Streamlit } from "streamlit-component-lib"
import { useStreamlit } from "./streamlit"

// Arguments that are passed to the plugin in Python are accessible in props
// "args".
const props = defineProps(["args"])
// Fetch changes to the default page, made by a callback function.
const selected = computed(() => props.args.default[0])
const activePage = ref(props.args.default[0])
console.log("selected", props.args.default)
console.log("left", props.args.left)
console.log("right", props.args.right)

useStreamlit()  // Lifecycle hooks for automatic Streamlit resize.

watch(selected, () => {
    // Executed when `selected` changes.
    activePage.value = selected.value
    console.log("active page", activePage)
  }
)

const onClicked = (page) => {
  /* remove the object proxy, so we can return it via streamlit */
  const p = JSON.parse(JSON.stringify(page));
  if (p === props.args.logo_page) {
    activePage.value = p;
    const time = props.args.allow_reselect ? Date.now() : null;
    Streamlit.setComponentValue([p, time]);
  } else if (p.url[0] === "#") {
    activePage.value = p.key;
    const time = props.args.allow_reselect ? Date.now() : null;
    Streamlit.setComponentValue([p.key, time]);
  }
}


const styles = ref(props.args.styles || {})
const css = ref(props.args.css)

const parseStyles = (dictionary, condition) => {
  if (typeof condition === "undefined") {
    condition = true
  }
  if (!condition) {
    return ""
  }
  let styleString = ""
  for (const key in dictionary) {
    styleString += `${key}:${dictionary[key]};`
  }
  return styleString
}

let color = ""
let bgColor = ""
if ("hover" in styles.value) {
  const stylesHover = styles.value["hover"]
  if ("color" in stylesHover) {
    color = stylesHover["color"]
  }
  if ("background-color" in stylesHover) {
    bgColor = stylesHover["background-color"]
  }
}
let hoverColor = ""
if (!(color === "")) {
  hoverColor = ref("hover-color")
}
let hoverBgColor = ""
if (!(bgColor === "")) {
  hoverBgColor = ref("hover-bg-color")
}
</script>

<style scoped>
@layer default {
div.navbar-right > ul {
  justify-content: right;
}

/* HTML tags */
* {
  margin: 0;
  padding: 0;
}
nav {
  align-items: center;
  background-color: var(--secondary-background-color);
  display: flex;
  font-family: var(--font);
  height: 2.875rem;
  justify-content: center;
  padding-left: 2rem;
  padding-right: 2rem;
}
div.navbar-left, div.navbar-right {
  max-width: 43.75rem;
  width: 100%;
}
ul {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
li {
  align-items: center;
  display: flex;
  list-style: none;
}
a {
  text-decoration: none;
}
img {
  display: flex;
  height: 1.875rem;
}

span.navbar-span {
  color: var(--text-color);
}

div.navbar-text {
  display: block;
  text-align: center;
}

/* Special class that acts as an :active pseudo-class for <span> */
.active {
  color: var(--text-color);
  -webkit-text-stroke-width: 0.5px;
}

/* Both classes with :hover direct the style to <span> */
.hover-color:hover {
  color: v-bind(color) !important;
}
.hover-bg-color:hover {
  background-color: v-bind(bgColor) !important;
}
}
</style>
