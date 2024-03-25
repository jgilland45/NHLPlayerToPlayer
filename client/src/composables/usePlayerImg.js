import { computed, ref, ComputedRef } from 'vue'

export const getHeadshotFromUrl = (imgUrl) => {
    const loadImg = ref(false)
    const img = computed(() => new Image())
    img.value.src = imgUrl.value
    img.value.onload = () => {
        loadImg.value = true
        console.log('image loaded')
    }
    img.value.onerror = () => {
        loadImg.value = false
        console.log('image errored')
    }
    console.log('final loadImg: ', loadImg)
    const newImgUrl = computed(() => loadImg.value ? imgUrl.value : 'https://assets.nhle.com/mugs/nhl/default-skater.png')
    console.log(newImgUrl.value)
    return { newPlayerImgUrL: newImgUrl }
}
