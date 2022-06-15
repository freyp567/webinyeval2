// models.ts - for mybooksdb
// adapted from https://www.webiny.com/docs/headless-cms/extending/content-models-via-code#create-content-model-group-and-content-model-plugins

import { CmsModelPlugin } from "@webiny/api-headless-cms/content/plugins/CmsModelPlugin"
import { CmsGroupPlugin } from "@webiny/api-headless-cms/content/plugins/CmsGroupPlugin"

export default [
  // "MyBooksDB" content models group.
  new CmsGroupPlugin({
    id: "mybooksdb",
    name: "MyBooksDB",
    description: "MyBooksDB",
    slug: "mybooksdb",
    icon: "fas/book"
  }),

  // "BookItem" content model.
  new CmsModelPlugin({
    name: "BookItem",
    description: "book item",
    modelId: "bookitem",
    group: {
      id: "mybooksdb",
      name: "MyBooksDB"
    },
    fields: [
      {
        id: "bookId",
        fieldId: "bookId",
        type: "text",
        label: "Book Id",
        helpText: "unique id of book item",
        renderer: { name: "text-input" },
        validation: [
          {
            name: "required",
            message: "id is required."
          },
        ],
      },
      {
        id: "bookTitle",
        fieldId: "bookTitle",
        type: "text",
        label: "Title",
        placeholderText: "title of book",
        renderer: { name: "text-input" },
        validation: [
          {
            name: "required",
            message: "title is required."
          },
        ]
      },
      {
        id: "dateRead",
        fieldId: "dateRead",
        type: "datetime",
        label: "date read",
        settings: {
          "type": "date"
        },
        renderer: { name: "text-input" }
      }
    ],
    layout: [["bookTitle"], ["dateRead"]],
    titleFieldId: "bookTitle"
  }),
]


//
