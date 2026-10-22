"use client"

import React, { useState } from "react"
import { useAuth, UserButton } from "@clerk/nextjs"
import Image from "next/image"
import {
  Activity,
  ArrowUpRight,
  Check,
  Code,
  Film,
  Fingerprint,
  Globe,
  Home,
  Layers,
  Link2,
  Plus,
  Radio,
  RefreshCw,
  Trophy,
  Upload,
  X,
} from "lucide-react"

import {
  createSource,
  listTheSources,
  removeTheCreateStoreSource,
  updateCreateStore,
} from "@/features/sourceSlice"
import { useAppDispatch, useAppSelector } from "@/lib/redux/hook"
import { source_scope } from "@/types/source"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Field, FieldLabel } from "@/components/ui/field"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { Spinner } from "@/components/ui/spinner"

const scopeOptions: {
  id: source_scope
  label: string
  description: string
  icon: typeof Code
  activeClass: string
  iconClass: string
}[] = [
  {
    id: "Technical",
    label: "Technical",
    description: "Tech & development",
    icon: Code,
    activeClass:
      "border-sky-500/40 bg-sky-500/10 text-sky-700 dark:text-sky-300",
    iconClass: "text-sky-600 dark:text-sky-400",
  },
  {
    id: "Sports",
    label: "Sports",
    description: "Sports & athletics",
    icon: Trophy,
    activeClass:
      "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
    iconClass: "text-emerald-600 dark:text-emerald-400",
  },
  {
    id: "Cinema",
    label: "Cinema",
    description: "Movies & media",
    icon: Film,
    activeClass:
      "border-fuchsia-500/40 bg-fuchsia-500/10 text-fuchsia-700 dark:text-fuchsia-300",
    iconClass: "text-fuchsia-600 dark:text-fuchsia-400",
  },
]

function Page() {
  const [newSource, setNewSource] = useState<{
    source_name: string
    source_url: string
    source_type: string
    nationality: string
    source_scope: source_scope
    crawl_pattern: string
  }>({
    source_name: "",
    source_url: "",
    source_type: "",
    nationality: "",
    source_scope: "Technical",
    crawl_pattern: "",
  })

  const { getToken } = useAuth()
  const { createSources } = useAppSelector((state) => state.source)
  const dispatch = useAppDispatch()
  const stagedCount = createSources.data.length
  const coverageCount = new Set(
    createSources.data.map((source) => source.source_scope)
  ).size

  const handleSourceAddition = (e: React.FormEvent) => {
    e.preventDefault()

    dispatch(
      updateCreateStore({
        sourceDetails: newSource,
      })
    )

    setNewSource({
      source_name: "",
      source_url: "",
      source_type: "",
      nationality: "",
      source_scope: "Technical",
      crawl_pattern: "",
    })
  }

  const uploadTheSources = async () => {
    const clerkJwtToken = await getToken()

    dispatch(
      createSource({
        token: clerkJwtToken || "",
      })
    )
    dispatch(
      listTheSources({
        token: clerkJwtToken || "",
      })
    )
  }

  const handleRemoveSource = (index: number) => {
    dispatch(removeTheCreateStoreSource({ index }))
  }

  return (
    <div className="min-h-screen bg-muted/30 text-foreground">
      <header className="sticky top-0 z-40 border-b border-border/80 bg-background backdrop-blur-xl">
        <div className="mx-auto flex h-[68px] max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex size-9 items-center justify-center rounded-xl bg-primary shadow-sm shadow-primary/20">
              <Image
                src="/logo.png"
                alt="PulseGrid"
                width={24}
                height={24}
                className="size-6 dark:invert"
              />
            </div>
            <div className="flex items-center gap-2">
              <span className="font-heading text-base font-bold tracking-tight">
                PulseGrid
              </span>
              <span className="hidden h-4 w-px bg-border sm:block" />
              <span className="hidden text-sm text-muted-foreground sm:block">
                Control room
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/5 px-3 py-1.5 sm:flex">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-500/50" />
                <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
              </span>
              <span className="text-xs font-medium text-emerald-700 dark:text-emerald-400">
                Ingestion active
              </span>
            </div>
            <UserButton />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1440px] px-4 pt-8 pb-12 sm:px-6 sm:pt-10 lg:px-8">
        <div className="mb-7 flex items-center gap-2 text-xs font-medium text-muted-foreground">
          <span>Infrastructure</span>
          <span className="text-border">/</span>
          <span className="text-foreground">Sources</span>
        </div>

        <div className="grid items-start gap-6 xl:grid-cols-[minmax(360px,0.9fr)_minmax(0,1.35fr)]">
          <section className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            <div className="border-b border-border px-5 py-5 sm:px-6">
              <div className="flex items-start gap-3">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Plus className="size-5" />
                </div>
                <div>
                  <h2 className="font-heading text-lg font-semibold tracking-tight">
                    Add a source
                  </h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Enter the details for a feed or publication.
                  </p>
                </div>
              </div>
            </div>

            <form
              onSubmit={handleSourceAddition}
              className="flex flex-col gap-5 p-5 sm:p-6"
            >
              <Field>
                <FieldLabel
                  htmlFor="source_name"
                  className="text-sm font-medium"
                >
                  Source name
                </FieldLabel>
                <InputGroup className="h-10 bg-background">
                  <InputGroupAddon align="inline-start">
                    <Globe className="size-4" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="source_name"
                    placeholder="e.g. TechCrunch"
                    value={newSource.source_name}
                    onChange={(e) =>
                      setNewSource({
                        ...newSource,
                        source_name: e.target.value,
                      })
                    }
                  />
                </InputGroup>
              </Field>

              <Field>
                <FieldLabel
                  htmlFor="source_url"
                  className="text-sm font-medium"
                >
                  Source URL
                </FieldLabel>
                <InputGroup className="h-10 bg-background">
                  <InputGroupAddon align="inline-start">
                    <Link2 className="size-4" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="source_url"
                    placeholder="e.g. https://techcrunch.com"
                    value={newSource.source_url}
                    onChange={(e) =>
                      setNewSource({ ...newSource, source_url: e.target.value })
                    }
                  />
                </InputGroup>
              </Field>

              <Field>
                <FieldLabel
                  htmlFor="source_pattern"
                  className="text-sm font-medium"
                >
                  Crawl pattern
                  <span className="font-normal text-muted-foreground">
                    {" "}
                    · optional
                  </span>
                </FieldLabel>
                <InputGroup className="h-10 bg-background">
                  <InputGroupAddon align="inline-start">
                    <Fingerprint className="size-4" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="source_pattern"
                    placeholder="Add a source regex pattern"
                    value={newSource.crawl_pattern}
                    onChange={(e) =>
                      setNewSource({
                        ...newSource,
                        crawl_pattern: e.target.value,
                      })
                    }
                  />
                </InputGroup>
              </Field>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Field>
                  <FieldLabel
                    htmlFor="source_type"
                    className="text-sm font-medium"
                  >
                    Type
                  </FieldLabel>
                  <InputGroup className="h-10 bg-background">
                    <InputGroupAddon align="inline-start">
                      <Radio className="size-4" />
                    </InputGroupAddon>
                    <InputGroupInput
                      id="source_type"
                      placeholder="International or national"
                      value={newSource.source_type}
                      onChange={(e) =>
                        setNewSource({
                          ...newSource,
                          source_type: e.target.value,
                        })
                      }
                    />
                  </InputGroup>
                </Field>

                <Field>
                  <FieldLabel
                    htmlFor="source_nationality"
                    className="text-sm font-medium"
                  >
                    Nationality
                  </FieldLabel>
                  <InputGroup className="h-10 bg-background">
                    <InputGroupAddon align="inline-start">
                      <Home className="size-4" />
                    </InputGroupAddon>
                    <InputGroupInput
                      id="source_nationality"
                      placeholder="e.g. India"
                      value={newSource.nationality}
                      onChange={(e) =>
                        setNewSource({
                          ...newSource,
                          nationality: e.target.value,
                        })
                      }
                    />
                  </InputGroup>
                </Field>
              </div>

              <fieldset>
                <legend className="mb-2 text-sm font-medium">
                  Source scope
                </legend>
                <div className="grid grid-cols-3 gap-2">
                  {scopeOptions.map((option) => {
                    const Icon = option.icon
                    const isSelected = newSource.source_scope === option.id

                    return (
                      <button
                        key={option.id}
                        type="button"
                        aria-pressed={isSelected}
                        onClick={() =>
                          setNewSource({
                            ...newSource,
                            source_scope: option.id,
                          })
                        }
                        className={`flex min-h-[92px] flex-col items-center justify-center gap-1 rounded-xl border px-2 py-3 text-center transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-none ${
                          isSelected
                            ? option.activeClass
                            : "border-border bg-background text-muted-foreground hover:border-primary/30 hover:bg-muted/60"
                        }`}
                      >
                        <Icon
                          className={`mb-1 size-5 ${isSelected ? "" : option.iconClass}`}
                        />
                        <span className="text-xs font-semibold">
                          {option.label}
                        </span>
                        <span className="hidden text-[10px] text-muted-foreground sm:block">
                          {option.description}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </fieldset>

              <Button type="submit" className="mt-1 h-11 w-full gap-2">
                <Plus className="size-4" />
                Add to queue
              </Button>
            </form>
          </section>

          <section className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            <div className="flex flex-col justify-between gap-4 border-b border-border px-5 py-5 sm:flex-row sm:items-center sm:px-6">
              <div className="flex items-start gap-3">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-secondary text-secondary-foreground">
                  <Layers className="size-5" />
                </div>
                <div>
                  <h2 className="font-heading text-lg font-semibold tracking-tight">
                    Deployment queue
                  </h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Review sources before sending them to the pipeline.
                  </p>
                </div>
              </div>
              <Badge variant="secondary" className="w-fit gap-1.5 px-2.5 py-1">
                <span className="size-1.5 rounded-full bg-primary" />
                {stagedCount} {stagedCount === 1 ? "source" : "sources"} staged
              </Badge>
            </div>

            <div className="p-5 sm:p-6">
              {stagedCount === 0 ? (
                <div className="flex min-h-[320px] flex-col items-center justify-center rounded-xl border border-dashed border-border bg-muted/20 px-6 py-10 text-center">
                  <div className="mb-4 flex size-14 items-center justify-center rounded-2xl bg-background text-muted-foreground shadow-sm">
                    <Layers className="size-6" />
                  </div>
                  <h3 className="font-heading text-base font-semibold">
                    Your queue is clear
                  </h3>
                  <p className="mt-2 max-w-sm text-sm leading-6 text-muted-foreground">
                    Add a source with the form to the left. It will appear here
                    for review before deployment.
                  </p>
                  <div className="mt-5 flex items-center gap-2 text-xs font-medium text-muted-foreground">
                    <Activity className="size-3.5 text-emerald-600 dark:text-emerald-400" />
                    Ready for new sources
                  </div>
                </div>
              ) : (
                <div className="max-h-[460px] space-y-3 overflow-y-auto pr-1">
                  {createSources.data.map((source, index) => {
                    const scopeOption = scopeOptions.find(
                      (option) => option.id === source.source_scope
                    )
                    const Icon = scopeOption?.icon ?? Globe

                    return (
                      <article
                        key={`${source.source_name}-${index}`}
                        className="group rounded-xl border border-border bg-background p-4 transition-colors hover:border-primary/20 hover:bg-muted/20"
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`flex size-10 shrink-0 items-center justify-center rounded-xl border border-current/10 bg-muted/60 ${
                              scopeOption?.iconClass ?? "text-muted-foreground"
                            }`}
                          >
                            <Icon className="size-4.5" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <h3 className="truncate text-sm font-semibold">
                                {source.source_name || "Untitled source"}
                              </h3>
                              <Badge variant="outline" className="text-[10px]">
                                {source.source_scope}
                              </Badge>
                            </div>
                            <a
                              href={source.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="mt-1 inline-flex max-w-full items-center gap-1 truncate text-xs text-muted-foreground transition-colors hover:text-primary"
                            >
                              <span className="truncate">
                                {source.source_url || "No URL provided"}
                              </span>
                              {source.source_url && (
                                <ArrowUpRight className="size-3 shrink-0" />
                              )}
                            </a>
                            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
                              {source.source_type && (
                                <span>{source.source_type}</span>
                              )}
                              {source.nationality && (
                                <span>{source.nationality}</span>
                              )}
                              {source.crawl_pattern && (
                                <span className="max-w-full truncate font-mono text-[11px]">
                                  Pattern: {source.crawl_pattern}
                                </span>
                              )}
                            </div>
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            aria-label={`Remove ${source.source_name || "source"} from queue`}
                            title="Remove source"
                            onClick={() => handleRemoveSource(index)}
                            className="shrink-0 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                          >
                            <X className="size-4" />
                          </Button>
                        </div>
                      </article>
                    )
                  })}
                </div>
              )}

              {stagedCount > 0 && (
                <div className="mt-5 flex flex-col gap-4 border-t border-border pt-5 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-start gap-2.5 text-xs leading-5 text-muted-foreground">
                    <Check className="mt-0.5 size-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
                    <span>
                      Queue reviewed. Sources will be submitted together as one
                      batch.
                    </span>
                  </div>
                  <Button
                    type="button"
                    onClick={uploadTheSources}
                    disabled={createSources.isLoading}
                    className="h-11 w-full gap-2 bg-emerald-600 text-white hover:bg-emerald-700 sm:w-auto"
                  >
                    {createSources.isLoading ? (
                      <>
                        <Spinner className="text-white" />
                        Uploading…
                      </>
                    ) : (
                      <>
                        <Upload className="size-4" />
                        Deploy {stagedCount}{" "}
                        {stagedCount === 1 ? "source" : "sources"}
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </section>
        </div>

        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-muted-foreground">
          <RefreshCw className="size-3.5" />
          Sources are validated by the ingestion pipeline after deployment
        </div>
      </main>
    </div>
  )
}

export default Page
