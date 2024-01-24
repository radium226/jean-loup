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