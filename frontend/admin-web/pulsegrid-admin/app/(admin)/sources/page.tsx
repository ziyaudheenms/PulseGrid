import React from "react"
import { Field, FieldDescription, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { IconGlobe, IconOption, IconUpload, IconWorld, IconWorldSearch } from "@tabler/icons-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"




function page() {
  return (
    <div className="mx-auto flex items-center justify-between gap-3 px-16">
      <div className="flex flex-col justify-center w-[48%] h-screen">
        <div className="">
          <h1 className="text-4xl font-bold">Add Sources</h1>
          <p className="text-lg font-light text-gray-600 italic">
            Add new sources to fuel up the pulsegrid data pipeline.
          </p>
        </div>
        <div className="my-10 w-[60%]">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border">
                  <IconGlobe className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- TechCrunch"
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border">
                  <IconWorldSearch className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- www.TechCrunch.com"
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="border-color-border flex h-10 w-12 items-center justify-center rounded-full border">
                  <IconWorld className="text-2xl" stroke={2} />
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full rounded-2xl py-5"
                  placeholder="eg:- International or National"
                />
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger render={<Button variant="outline" />}>
                Open
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuGroup>
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuItem>Profile</DropdownMenuItem>
                  <DropdownMenuItem>Billing</DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                  <DropdownMenuItem>Team</DropdownMenuItem>
                  <DropdownMenuItem>Subscription</DropdownMenuItem>
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
            </div>

          <Button className="mt-5 w-full flex items-center gap-2 py-5">
            <IconUpload stroke={2} className="text-xl"/>
            Add Source
          </Button>
        </div>

      </div>
      <div>
        <h1 className="text-4xl font-bold">Add Sources</h1>
        <p className="text-lg font-light text-gray-600 italic">
          Add new sources to fuel up the pulsegrid data pipeline.
        </p>
      </div>
    </div>
  )
}

export default page
