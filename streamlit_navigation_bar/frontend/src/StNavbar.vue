<template>
  <section>
  <link rel="stylesheet"
    type="text/css"
    href="https://fonts.googleapis.com/icon?family=Material+Icons">

  <component v-if="css" :is="'style'">
  @scope {
      {{ css }}
  }
  </component>

  <nav 
      class="streamlit-navbar"
      :style="parseStyles(styles['nav'])">
    <div 
      class="streamlit-navbar-left streamlit-navbar-group"
      :style="parseStyles(styles['div'])">
      <ul :style="parseStyles(styles['ul'])"
	class="streamlit-navbar-list">
        <li
          v-if="args.base64_svg"
          :style="parseStyles(styles['li'])"
	  class="streamlit-navbar-item"
        >
          <a
            v-if="args.logo_page"
            href="#"
	    class="streamlit-navbar-anchor"
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
	    class="streamlit-navbar-anchor"
            :style="parseStyles(styles['a'])"
          >
            <img
	      class="streamlit-navbar-logo"
              :src="`data:image/svg+xml; base64, ${args.base64_svg}`"
              :style="parseStyles(styles['img'])"
            />
          </a>
        </li>
        <li
          v-for="page in args.left"
	  class="streamlit-navbar-item"
          :key="page"
          :style="parseStyles(styles['li'])"
        >
          <a
            :href="`${args.urls[page][0]}`"
            :target="`${args.urls[page][1]}`"
            :style="parseStyles(styles['a'])"
	    class="streamlit-navbar-anchor"
            @click="onClicked(page)"
          >
            <span
              :data-text="page"
              :class="[{active: page === activePage}, hoverColor, hoverBgColor]"
              :style="parseStyles(styles['span']) + parseStyles(styles['active'], page === activePage)"
	      class="streamlit-navbar-span"
	      style="display: inline-block;"
            >
              <div 
                v-if="page in args.icons"
                class="material-icons streamlit-navbar-icon"
                style="display: inline; vertical-align: middle"
              >
                {{ args.icons[page] }} 
	      </div>
              <div class="streamlit-navbar-text" style="display: inline; vertical-align: middle; margin-left: 0.35em">
	        {{ page }}
              </div>
            </span>
          </a>
        </li>
      </ul>
    </div>
    <div 
      v-if="args.right.length"
      class="streamlit-navbar-right streamlit-navbar-group"
      :style="parseStyles(styles['div'])">
      <ul :style="parseStyles(styles['ul'])"
	class="streamlit-navbar-list">
        <li
          v-for="page in args.right"
	  class="streamlit-navbar-item"
          :key="page"
          :style="parseStyles(styles['li'])"
        >
          <a
            :href="`${args.urls[page][0]}`"
            :target="`${args.urls[page][1]}`"
            :style="parseStyles(styles['a'])"
	    class="streamlit-navbar-anchor"
            @click="onClicked(page)"
          >
            <span
              :data-text="page"
              :class="[{active: page === activePage}, hoverColor, hoverBgColor]"
              :style="parseStyles(styles['span']) + parseStyles(styles['active'], page === activePage)"
	      class="streamlit-navbar-span"
	      style="display: inline-block"
            >
              <div 
                v-if="page in args.icons"
                class="material-icons streamlit-navbar-icon"
                style="display: inline; vertical-align: middle"
              >
                {{ args.icons[page] }} 
              </div>
	      <div class="streamlit-navbar-text" style="display: inline; vertical-align: middle; margin-left: 0.35em">
              {{ page }}
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
const selected = computed(() => props.args.default)
const activePage = ref(props.args.default)

useStreamlit()  // Lifecycle hooks for automatic Streamlit resize.

watch(selected, () => {
    // Executed when `selected` changes.
    activePage.value = selected.value
  }
)

const onClicked = (page) => {
  if (page === props.args.logo_page || props.args.urls[page][0] === "#") {
    activePage.value = page
    Streamlit.setComponentValue(page)
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
div.streamlit-navbar-right > ul {
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
div.streamlit-navbar-left, div.streamlit-navbar-right {
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
span.streamlit-navbar-page {
  color: var(--text-color);
  display: block;
  text-align: center;
}

/* Special class that acts as an :active pseudo-class for <span> */
.active {
  color: var(--text-color);
  font-weight: bold;
}

/* Stop the page names from moving when the active <span> is set to bold */
span.streamlit-navbar-text::before {
  content: attr(data-text);
  display: flex;
  font-weight: bold;
  height: 0;
  overflow: hidden;
  pointer-events: none;
  user-select: none;
  visibility: hidden;
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
