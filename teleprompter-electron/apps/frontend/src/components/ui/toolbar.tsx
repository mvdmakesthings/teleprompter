import * as React from "react"
import { cn } from "@/lib/utils"

interface ToolbarProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical"
}

const Toolbar = React.forwardRef<HTMLDivElement, ToolbarProps>(
  ({ className, orientation = "horizontal", ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "flex items-center space-x-2 rounded-md border bg-background p-1",
        orientation === "vertical" && "flex-col space-x-0 space-y-2",
        className
      )}
      {...props}
    />
  )
)
Toolbar.displayName = "Toolbar"

interface ToolbarGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical"
}

const ToolbarGroup = React.forwardRef<HTMLDivElement, ToolbarGroupProps>(
  ({ className, orientation = "horizontal", ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "flex items-center space-x-1",
        orientation === "vertical" && "flex-col space-x-0 space-y-1",
        className
      )}
      {...props}
    />
  )
)
ToolbarGroup.displayName = "ToolbarGroup"

const ToolbarSeparator = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("mx-1 h-4 w-[1px] bg-border", className)}
    {...props}
  />
))
ToolbarSeparator.displayName = "ToolbarSeparator"

export { Toolbar, ToolbarGroup, ToolbarSeparator }