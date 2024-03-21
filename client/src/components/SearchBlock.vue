<template>
  <table v-if="filteredData.length && filterKey.length > 2">
    <thead>
      <tr>
        <th v-for="key in columns"
          @click="sortBy(key)"
          :class="{ active: sortKey == key }"
          :key="key">
          {{ capitalize(key) }}
          <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
          </span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="entry in filteredData"
      :key="entry.url"
      @click="onRowClick(entry)">
        <td v-for="key in columns"
        :key="key">
          {{ entry[key] }}
        </td>
      </tr>
    </tbody>
  </table>
  <p v-else>No matches found.</p>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  data: Array,
  columns: Array,
  filterKey: String
})

const emit = defineEmits(['choose'])

const onRowClick = (player) => {
  emit('choose', player)
}

const sortKey = ref('')
const sortOrders = ref(props.columns.reduce((o, key) => (((o[key] = 1), o)), {}))

const filteredData = computed(() => {
  let { data, filterKey } = props
  if (filterKey) {
    // https://stackoverflow.com/questions/990904/remove-accents-diacritics-in-a-string-in-javascript
    filterKey = filterKey.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
    data = data.filter((row) => {
      return Object.keys(row).some((key) => {
        return String(row[key]).normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().indexOf(filterKey) > -1
      })
    })
  }
  const key = sortKey.value
  if (key) {
    const order = sortOrders.value[key]
    data = data.slice().sort((a, b) => {
      a = a[key]
      b = b[key]
      return (a === b ? 0 : a > b ? 1 : -1) * order
    })
  }
  return data
})

function sortBy (key) {
  sortKey.value = key
  sortOrders.value[key] *= -1
}

function capitalize (str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}
</script>

<style lang="postcss" scoped>
table {
  border: 2px solid #42b983;
  border-radius: 3px;
  background-color: #fff;
}

th {
  background-color: #42b983;
  color: rgba(255, 255, 255, 0.66);
  cursor: pointer;
  user-select: none;
}

td {
  background-color: #f9f9f9;
}

th,
td {
  min-width: 120px;
  padding: 10px 20px;
}

th.active {
  color: #fff;
}

th.active .arrow {
  opacity: 1;
}

tr:hover {
  color:#42b983;
  text-decoration: underline;
  cursor: pointer;
}

.arrow {
  display: inline-block;
  vertical-align: middle;
  width: 0;
  height: 0;
  margin-left: 5px;
  opacity: 0.66;
}

.arrow.asc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid #fff;
}

.arrow.dsc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #fff;
}
</style>
