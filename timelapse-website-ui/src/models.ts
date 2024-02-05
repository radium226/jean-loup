import { z } from "zod"

export enum PictureIntent {
    TimeLapse,
    AdHoc,
}

export interface Picture {
    id: string
    dateTime: Date
    intent: PictureIntent
}

export function formatPicture(picture: Picture): string {
    return JSON.stringify(z.object({
        id: z.string(),
        dateTime: z.date(),
        intent: z.nativeEnum(PictureIntent),
    }).transform(({ id, dateTime, intent }) => ({
        id,
        intent: {
            [PictureIntent.TimeLapse]: "time_lapse",
            [PictureIntent.AdHoc]: "ad_hoc",
        }[intent],
        date_time: dateTime.toISOString(),
    })).parse(picture))
}

export function parsePicture(input: any): Picture {
    return z.object({
        id: z.string(),
        date_time: z.string(),
        intent: z
            .enum(["time_lapse", "ad_hoc"])
            .transform((value) => {
                return {
                    "time_lapse": PictureIntent.TimeLapse,
                    "ad_hoc": PictureIntent.AdHoc,
                }[value]
            })
    }).transform(({ id, date_time, intent }) => ({
        id,
        dateTime: new Date(date_time),
        intent,
    })).parse(input)
}


export interface ConfigValues {
    hotspot: {
        enabled: boolean,
        ssid: string,
        password?: string,
    },
    timeLapse: {
        enabled: boolean, 
    },
}


export function parseConfigValues(input: any): ConfigValues {
    return z.object({
        time_lapse: z.object({
            enabled: z.boolean(),
            wakeup_time: z.string(),
        }),
        hotspot: z.object({
            enabled: z.boolean(),
            ssid: z.string(),
            password: z.string().optional(),
        })
    }).transform((pythonConfigValues) => ({
        timeLapse: {
            enabled: pythonConfigValues.time_lapse.enabled,
            wakeupTime: pythonConfigValues.time_lapse.wakeup_time,
        },
        hotspot: {
            enabled: pythonConfigValues.hotspot.enabled,
            ssid: pythonConfigValues.hotspot.ssid,
            password: pythonConfigValues.hotspot.password,
        },
    })).parse(input)

}

export function formatConfigValues(configValues: ConfigValues): string {
    return JSON.stringify(z.object({
        hotspot: z.object({
            enabled: z.boolean(),
            ssid: z.string(),
            password: z.string().optional(),
        }),
        timeLapse: z.object({
            enabled: z.boolean(),
        }),
    }).transform(({ hotspot, timeLapse }) => ({
        hotspot: {
            enabled: hotspot.enabled,
            ssid: hotspot.ssid,
            password: hotspot.password,
        },
        time_lapse: {
            enabled: timeLapse.enabled,
        },
    })).parse(configValues))
}