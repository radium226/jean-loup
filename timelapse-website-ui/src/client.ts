import { Picture, parsePicture, ConfigValues, parseConfigValues, formatConfigValues } from "./models"


export class Client {

    public baseURL: string

    constructor(baseURL: string = "/api") {
        this.baseURL = baseURL
    }

    async takePicture(): Promise<Picture> {
        const response = await fetch(`${this.baseURL}/pictures`, {
            method: "POST",
        })
        const json = await response.json()
        const picture = parsePicture(json)
        console.log(picture)
        return picture
    }

    async downloadPictureContent(picture: Picture): Promise<Blob> {
        const baseURL = this.baseURL
        const url = `${baseURL}/pictures/${picture.id}/content`
        console.log(url)
        const response = await fetch(url, {
            method: "GET",
        })
        const blob = await response.blob()
        return blob;
    }

    async downloadPictureThumbnail(picture: Picture): Promise<Blob> {
        const baseURL = this.baseURL
        const url = `${baseURL}/pictures/${picture.id}/thumbnail`
        console.log(url)
        const response = await fetch(url, {
            method: "GET",
        })
        const blob = await response.blob()
        return blob;
    }

    async listPictures(): Promise<Picture[]> {
        const response = await fetch(`${this.baseURL}/pictures`, {
            method: "GET",
        })
        const jsons: any[] = await response.json();
        return jsons.map((json) => parsePicture(json))
    }

    async readConfigValues(): Promise<ConfigValues> {
        const response = await fetch(`${this.baseURL}/config_values`, {
            method: "GET"
        })
        const json = await response.json();
        return parseConfigValues(json)
    }

    async writeConfigValues(configValues: ConfigValues): Promise<void> {
        fetch(`${this.baseURL}/config`, {
            method: "PUT",
            body: JSON.stringify(formatConfigValues(configValues)),
            headers: {
                "Content-Types": "application/json",
            },
        })
    }
    
}