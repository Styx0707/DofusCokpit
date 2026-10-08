on(construct){
   while(true)
   {
      if(!(0x122B162B & 0x122B162B))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownLeftSmallLabel";
         §§push("text");
         §§push("");
         if(!(getTimer() + 1))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addrf911);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addrf911:
}
